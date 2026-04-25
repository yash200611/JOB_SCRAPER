import logging
import re
import time
from datetime import datetime, timezone
from typing import List, Dict

import requests

from config import CUTOFF_DATE, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF
from utils.filters import match_location, match_title, is_blocked

logger = logging.getLogger(__name__)

ALGOLIA_SEARCH_URL = (
    "https://hn.algolia.com/api/v1/search_by_date"
    "?query=who+is+hiring&tags=ask_hn&hitsPerPage=5"
)
HN_ITEMS_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"


def _get_with_retry(url: str) -> dict | None:
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2 ** attempt))
            else:
                logger.error(f"HN fetch failed {url}: {e}")
    return None


def _extract_url(text: str) -> str:
    match = re.search(r"https?://\S+", text)
    return match.group(0).rstrip("|>).,") if match else ""


def _extract_company(text: str) -> str:
    # First line of HN comment typically starts with "Company Name | ..."
    first_line = text.split("\n")[0].split("|")[0].strip()
    # Strip HTML tags
    return re.sub(r"<[^>]+>", "", first_line).strip()


def _get_latest_hiring_thread_id() -> int | None:
    data = _get_with_retry(ALGOLIA_SEARCH_URL)
    if not data:
        return None
    hits = data.get("hits", [])
    for hit in hits:
        title = hit.get("title", "").lower()
        if "who is hiring" in title:
            return hit.get("objectID")
    return None


def scrape() -> List[Dict]:
    results = []

    thread_id = _get_latest_hiring_thread_id()
    if not thread_id:
        logger.error("HN: could not find latest who's hiring thread")
        return results

    thread = _get_with_retry(HN_ITEMS_URL.format(thread_id))
    if not thread:
        return results

    comment_ids = thread.get("kids", [])[:200]  # top 200 comments

    for cid in comment_ids:
        time.sleep(0.1)  # gentle rate limit
        comment = _get_with_retry(HN_ITEMS_URL.format(cid))
        if not comment:
            continue

        text_raw = comment.get("text", "") or ""
        text = re.sub(r"<[^>]+>", " ", text_raw).replace("&#x27;", "'").replace("&amp;", "&")
        text_lower = text.lower()

        if "intern" not in text_lower:
            continue

        if not match_title(text_lower):
            # check first 200 chars for a role keyword hit
            if not any(kw in text_lower[:300] for kw in ["intern"]):
                continue

        city = match_location(text)
        if not city:
            continue

        company = _extract_company(text)
        if not company or is_blocked(company):
            continue

        created_ts = comment.get("time")
        dt = None
        date_str = "unknown"
        if created_ts:
            dt = datetime.fromtimestamp(created_ts, tz=timezone.utc)
            if dt < CUTOFF_DATE:
                continue
            date_str = dt.date().isoformat()

        apply_url = _extract_url(text) or f"https://news.ycombinator.com/item?id={cid}"

        results.append({
            "company_name": company,
            "company_stage": "unknown",
            "role_title": "Internship (see posting)",
            "location": city,
            "date_posted": date_str,
            "application_url": apply_url,
            "source": "hackernews",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })

    logger.info(f"HN: {len(results)} jobs found")
    return results
