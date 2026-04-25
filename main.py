#!/usr/bin/env python3
import logging
import os
import sys

# Allow imports from project root
sys.path.insert(0, os.path.dirname(__file__))

from scrapers import greenhouse, lever, ashby, yc, wellfound, hackernews
from utils.dedup import deduplicate
from utils.export import save_csv, print_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("main")


def run():
    logger.info("Starting job scraper run")
    all_jobs = []

    sources = [
        ("greenhouse", greenhouse.scrape),
        ("lever", lever.scrape),
        ("ashby", ashby.scrape),
        ("yc", yc.scrape),
        ("wellfound", wellfound.scrape),
        ("hackernews", hackernews.scrape),
    ]

    for name, scrape_fn in sources:
        try:
            jobs = scrape_fn()
            all_jobs.extend(jobs)
            logger.info(f"{name}: collected {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"{name} scraper raised unexpected error: {e}", exc_info=True)

    deduped = deduplicate(all_jobs)
    logger.info(f"After dedup: {len(deduped)} unique jobs (from {len(all_jobs)} total)")

    csv_path = save_csv(deduped)
    print_summary(deduped, csv_path)


if __name__ == "__main__":
    run()
