import os
from datetime import date
from typing import List, Dict
import pandas as pd

COLUMNS = [
    "company_name", "company_stage", "role_title", "location",
    "date_posted", "application_url", "source", "scraped_at",
]

ROLE_CATEGORIES = {
    "SWE": [
        "software", "full stack", "fullstack", "full-stack", "backend", "back-end",
        "frontend", "front-end", "platform", "infrastructure", "devops",
        "site reliability", "mobile", "ios", "android", "web developer", "product engineer",
    ],
    "Data/Quant": [
        "data engineer", "data science", "data analyst", "quantitative", "quant",
        "machine learning", "ml engineer", "ai engineer", "analytics",
    ],
    "Finance": [
        "venture capital", "vc analyst", "investment", "equity research",
        "asset management", "portfolio", "financial analyst", "deal",
    ],
    "Consulting": ["strategy", "consulting", "operations", "business analyst", "biz ops"],
}


def _categorize(title: str) -> str:
    t = title.lower()
    for cat, keywords in ROLE_CATEGORIES.items():
        if any(kw in t for kw in keywords):
            return cat
    return "Other"


def save_csv(jobs: List[Dict], output_dir: str = "results") -> str:
    os.makedirs(output_dir, exist_ok=True)
    today = date.today().isoformat()
    path = os.path.join(output_dir, f"jobs_{today}.csv")

    rows = []
    for j in jobs:
        rows.append({col: j.get(col, "unknown") for col in COLUMNS})

    df = pd.DataFrame(rows, columns=COLUMNS)
    df.to_csv(path, index=False)
    return path


def print_summary(jobs: List[Dict], csv_path: str) -> None:
    today = date.today().isoformat()
    total = len(jobs)

    city_counts: Dict[str, int] = {}
    role_counts: Dict[str, int] = {}
    source_counts: Dict[str, int] = {}

    for j in jobs:
        city = j.get("location", "unknown")
        city_counts[city] = city_counts.get(city, 0) + 1

        cat = _categorize(j.get("role_title", ""))
        role_counts[cat] = role_counts.get(cat, 0) + 1

        src = j.get("source", "unknown").capitalize()
        source_counts[src] = source_counts.get(src, 0) + 1

    city_line = " | ".join(f"{c}: {n}" for c, n in sorted(city_counts.items()))
    role_line = " | ".join(f"{c}: {n}" for c, n in sorted(role_counts.items()))
    source_line = " | ".join(f"{s} ({n})" for s, n in sorted(source_counts.items()))

    print(f"\n=== Job Scraper Run: {today} ===")
    print(f"Total new postings found: {total}")
    print(f"  {city_line}")
    print(f"  {role_line}")
    print(f"  Sources: {source_line}")
    print(f"CSV saved to: {csv_path}\n")
