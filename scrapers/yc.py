import logging
import time
from datetime import datetime, timezone
from typing import List, Dict

from utils.filters import match_location, match_title, is_blocked

logger = logging.getLogger(__name__)


YC_URL = "https://www.workatastartup.com/jobs?role=intern"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


def scrape() -> List[Dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("playwright not installed — skipping YC scraper")
        return []

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=USER_AGENTS[0])
            page = context.new_page()

            page.goto(YC_URL, wait_until="networkidle", timeout=30000)
            time.sleep(2)

            # YC renders job cards — grab all job listing elements
            job_cards = page.query_selector_all("div.job-name, [data-job-id], .JobCard, .job-card")

            if not job_cards:
                # Fallback: grab via text content scan
                content = page.content()
                logger.warning(f"YC: no job cards found via selector, page length={len(content)}")
                browser.close()
                return results

            for card in job_cards:
                try:
                    title_el = card.query_selector(".job-title, h3, .title")
                    company_el = card.query_selector(".company-name, .company, h2")
                    location_el = card.query_selector(".location, .job-location")
                    link_el = card.query_selector("a")

                    title = title_el.inner_text().strip() if title_el else ""
                    company = company_el.inner_text().strip() if company_el else ""
                    location_raw = location_el.inner_text().strip() if location_el else ""
                    href = link_el.get_attribute("href") if link_el else ""
                    apply_url = f"https://www.workatastartup.com{href}" if href and href.startswith("/") else href or YC_URL

                    if not match_title(title):
                        continue
                    if is_blocked(company):
                        continue

                    city = match_location(location_raw)
                    if not city:
                        continue

                    results.append({
                        "company_name": company or "unknown",
                        "company_stage": "unknown",
                        "role_title": title,
                        "location": city,
                        "date_posted": "unknown",
                        "application_url": apply_url,
                        "source": "yc",
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception as e:
                    logger.warning(f"YC card parse error: {e}")

            browser.close()
            time.sleep(2)

    except Exception as e:
        logger.error(f"YC scraper failed: {e}")

    logger.info(f"YC: {len(results)} jobs found")
    return results
