import logging
import random
import time
from datetime import datetime, timezone
from typing import List, Dict

from utils.filters import match_location, match_title, is_blocked

logger = logging.getLogger(__name__)


WELLFOUND_URL = "https://wellfound.com/jobs?jobType=internship"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]


def scrape() -> List[Dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("playwright not installed — skipping Wellfound scraper")
        return []

    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=random.choice(USER_AGENTS))
            page = context.new_page()

            page.goto(WELLFOUND_URL, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Scroll to load more results
            for _ in range(3):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(1.5)

            job_cards = page.query_selector_all(
                "[data-test='JobListing'], .styles_component__Ey28k, .JobListingCard, [class*='JobCard']"
            )

            if not job_cards:
                logger.warning("Wellfound: no job cards found via selector")
                browser.close()
                return results

            for card in job_cards:
                try:
                    title_el = card.query_selector("[data-test='JobListing-title'], h2, .title, [class*='title']")
                    company_el = card.query_selector("[data-test='JobListing-company'], .company, [class*='company']")
                    location_el = card.query_selector("[data-test='JobListing-location'], .location, [class*='location']")
                    stage_el = card.query_selector("[class*='stage'], [class*='Stage'], .funding-stage")
                    link_el = card.query_selector("a")

                    title = title_el.inner_text().strip() if title_el else ""
                    company = company_el.inner_text().strip() if company_el else ""
                    location_raw = location_el.inner_text().strip() if location_el else ""
                    stage = stage_el.inner_text().strip() if stage_el else "unknown"
                    href = link_el.get_attribute("href") if link_el else ""
                    apply_url = f"https://wellfound.com{href}" if href and href.startswith("/") else href or WELLFOUND_URL

                    if not match_title(title):
                        continue
                    if is_blocked(company):
                        continue

                    city = match_location(location_raw)
                    if not city:
                        continue

                    results.append({
                        "company_name": company or "unknown",
                        "company_stage": stage,
                        "role_title": title,
                        "location": city,
                        "date_posted": "unknown",
                        "application_url": apply_url,
                        "source": "wellfound",
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception as e:
                    logger.warning(f"Wellfound card parse error: {e}")

            browser.close()
            time.sleep(3)

    except Exception as e:
        logger.error(f"Wellfound scraper failed: {e}")

    logger.info(f"Wellfound: {len(results)} jobs found")
    return results
