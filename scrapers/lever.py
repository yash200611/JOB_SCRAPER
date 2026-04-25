import logging
import time
from datetime import datetime, timezone
from typing import List, Dict

import requests

from config import LEVER_COMPANIES, CUTOFF_DATE, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF
from utils.filters import match_location, match_title, is_blocked

logger = logging.getLogger(__name__)



def _get_with_retry(url: str) -> list | None:
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2 ** attempt))
            else:
                logger.error(f"Lever fetch failed {url}: {e}")
    return None


def scrape() -> List[Dict]:
    results = []
    for company in LEVER_COMPANIES:
        url = f"https://api.lever.co/v0/postings/{company}"
        data = _get_with_retry(url)
        if not data or not isinstance(data, list):
            continue

        for job in data:
            title = job.get("text", "")
            categories = job.get("categories", {})
            location_raw = categories.get("location", "") or ""
            created_ms = job.get("createdAt")
            apply_url = job.get("hostedUrl", "")

            if not match_title(title):
                continue
            if is_blocked(company):
                continue

            city = match_location(location_raw)
            if not city:
                continue

            dt = None
            date_str = "unknown"
            if created_ms:
                dt = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc)
                if dt < CUTOFF_DATE:
                    continue
                date_str = dt.date().isoformat()

            results.append({
                "company_name": company,
                "company_stage": "unknown",
                "role_title": title,
                "location": city,
                "date_posted": date_str,
                "application_url": apply_url,
                "source": "lever",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

    logger.info(f"Lever: {len(results)} jobs found")
    return results
