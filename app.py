#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import sys
import threading
from datetime import datetime, timezone
from typing import AsyncGenerator

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler

from scrapers import greenhouse, lever, ashby, yc, wellfound, hackernews
from utils.dedup import deduplicate
from utils.export import save_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("app")

app = FastAPI(title="Job Scraper")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Shared state ---
_state = {
    "jobs": [],
    "last_run": None,
    "running": False,
    "run_count": 0,
}
_subscribers: list[asyncio.Queue] = []
_state_lock = threading.Lock()


def _run_scrape():
    with _state_lock:
        if _state["running"]:
            return
        _state["running"] = True

    logger.info("Scrape run started")
    all_jobs = []
    sources = [
        ("greenhouse", greenhouse.scrape),
        ("lever", lever.scrape),
        ("ashby", ashby.scrape),
        ("yc", yc.scrape),
        ("wellfound", wellfound.scrape),
        ("hackernews", hackernews.scrape),
    ]
    for name, fn in sources:
        try:
            jobs = fn()
            all_jobs.extend(jobs)
            logger.info(f"{name}: {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"{name} failed: {e}", exc_info=True)

    deduped = deduplicate(all_jobs)
    csv_path = save_csv(deduped)
    logger.info(f"Run complete: {len(deduped)} jobs → {csv_path}")

    with _state_lock:
        _state["jobs"] = deduped
        _state["last_run"] = datetime.now(timezone.utc).isoformat()
        _state["running"] = False
        _state["run_count"] += 1

    # Notify SSE subscribers
    payload = json.dumps({"type": "update", "count": len(deduped), "ts": _state["last_run"]})
    for q in list(_subscribers):
        try:
            q.put_nowait(payload)
        except Exception:
            pass


# --- Scheduler: run every 60 minutes ---
scheduler = BackgroundScheduler()
scheduler.add_job(_run_scrape, "interval", minutes=60, id="scrape", next_run_time=datetime.now())
scheduler.start()


@app.on_event("shutdown")
def _shutdown():
    scheduler.shutdown(wait=False)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/jobs")
async def get_jobs():
    with _state_lock:
        jobs = list(_state["jobs"])
        last_run = _state["last_run"]
        running = _state["running"]
    return JSONResponse({"jobs": jobs, "last_run": last_run, "running": running, "total": len(jobs)})


@app.post("/api/run")
async def trigger_run():
    t = threading.Thread(target=_run_scrape, daemon=True)
    t.start()
    return {"status": "started"}


@app.get("/stream")
async def sse_stream(request: Request) -> StreamingResponse:
    queue: asyncio.Queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    _subscribers.append(queue)

    async def generator() -> AsyncGenerator[str, None]:
        try:
            # Send current state immediately
            with _state_lock:
                payload = json.dumps({
                    "type": "init",
                    "count": len(_state["jobs"]),
                    "ts": _state["last_run"],
                    "running": _state["running"],
                })
            yield f"data: {payload}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=25)
                    yield f"data: {msg}\n\n"
                except asyncio.TimeoutError:
                    yield "data: {\"type\":\"ping\"}\n\n"
        finally:
            if queue in _subscribers:
                _subscribers.remove(queue)

    return StreamingResponse(generator(), media_type="text/event-stream")
