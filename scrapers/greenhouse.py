import logging
import time
from datetime import datetime, timezone
from typing import List, Dict

import requests

from config import GREENHOUSE_COMPANIES, CUTOFF_DATE, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF, COMPANY_STAGES
from utils.filters import match_location, is_eligible, is_blocked

logger = logging.getLogger(__name__)


def _get_with_retry(url: str) -> dict | list | None:
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2 ** attempt))
            else:
                logger.error(f"Greenhouse fetch failed {url}: {e}")
    return None


def _parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def scrape() -> List[Dict]:
    results = []
    for company in GREENHOUSE_COMPANIES:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
        data = _get_with_retry(url)
        if not data:
            continue

        jobs = data.get("jobs", []) if isinstance(data, dict) else data
        for job in jobs:
            title = job.get("title", "")
            location_raw = job.get("location", {}).get("name", "") or ""
            updated_at = job.get("updated_at", "")
            apply_url = job.get("absolute_url", "")
            company_display = job.get("company_name") or company

            # Pull plain-text description for degree/experience filtering
            content = job.get("content", "") or ""

            if is_blocked(company_display):
                continue
            if not is_eligible(title, content):
                continue

            city = match_location(location_raw)
            if not city:
                continue

            dt = _parse_date(updated_at)
            if dt and dt < CUTOFF_DATE:
                continue

            stage = COMPANY_STAGES.get(company.lower(), "unknown")

            results.append({
                "company_name": company_display,
                "company_stage": stage,
                "role_title": title,
                "location": city,
                "date_posted": dt.date().isoformat() if dt else "unknown",
                "application_url": apply_url,
                "source": "greenhouse",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

    logger.info(f"Greenhouse: {len(results)} jobs found")
    return results
