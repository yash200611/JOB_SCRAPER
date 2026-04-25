import logging
import re
import time
from datetime import datetime, timezone
from typing import List, Dict

import requests

from config import ASHBY_COMPANIES, CUTOFF_DATE, REQUEST_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF, COMPANY_STAGES
from utils.filters import match_location, is_eligible, is_blocked

logger = logging.getLogger(__name__)


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
                logger.error(f"Ashby fetch failed {url}: {e}")
    return None


def _parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html)


def scrape() -> List[Dict]:
    results = []
    for company in ASHBY_COMPANIES:
        url = f"https://api.ashbyhq.com/posting-api/job-board/{company}"
        data = _get_with_retry(url)
        if not data:
            continue

        jobs = data.get("jobs", data.get("jobPostings", []))
        for job in jobs:
            title = job.get("title", "")
            location_raw = job.get("location", "") or ""
            published_date = job.get("publishedAt", "") or job.get("publishedDate", "")
            apply_url = job.get("applyUrl", "") or job.get("jobUrl", "") or ""
            description = _strip_html(job.get("descriptionHtml", "") or job.get("descriptionPlain", "") or "")

            if is_blocked(company):
                continue
            if not is_eligible(title, description):
                continue

            city = match_location(location_raw)
            if not city:
                continue

            dt = _parse_date(published_date)
            if dt and dt < CUTOFF_DATE:
                continue

            job_url = job.get("jobUrl", "")
            if "ashbyhq.com/" in job_url:
                slug_from_url = job_url.split("ashbyhq.com/")[-1].split("/")[0]
                company_display = slug_from_url.replace("-", " ").title()
            else:
                company_display = company.replace("-", " ").title()

            stage = COMPANY_STAGES.get(company.lower(), "unknown")

            results.append({
                "company_name": company_display,
                "company_stage": stage,
                "role_title": title,
                "location": city,
                "date_posted": dt.date().isoformat() if dt else "unknown",
                "application_url": apply_url,
                "source": "ashby",
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

    logger.info(f"Ashby: {len(results)} jobs found")
    return results
