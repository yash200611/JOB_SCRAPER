# Job Scraper

Production-ready internship scraper with a live web UI. Finds summer internships at startups across Greenhouse, Lever, Ashby, YC, Wellfound, and Hacker News. Runs hourly, deduplicates across sources, exports CSV.

## Setup

```bash
pip3 install -r requirements.txt
playwright install chromium
```

## Run

**Web UI (recommended):**
```bash
python3 -m uvicorn app:app --port 8080
# open http://localhost:8080
```

**CLI only:**
```bash
python3 main.py
```

## Project Structure

```
job-scraper/
├── app.py              # FastAPI web server + scheduler
├── main.py             # CLI entry point
├── config.py           # Locations, keywords, blocklist, company boards
├── scrapers/
│   ├── greenhouse.py   # Greenhouse public API
│   ├── lever.py        # Lever public API
│   ├── ashby.py        # Ashby public API
│   ├── yc.py           # Y Combinator Work at a Startup (Playwright)
│   ├── wellfound.py    # Wellfound / AngelList (Playwright)
│   └── hackernews.py   # HN "Who's Hiring" thread
├── utils/
│   ├── filters.py      # Title, location, blocklist matching
│   ├── dedup.py        # Cross-source deduplication
│   └── export.py       # CSV export + terminal summary
├── templates/
│   └── index.html      # AG Grid UI with SSE live updates
├── results/            # Output CSVs (gitignored)
└── logs/               # scraper.log (gitignored)
```

## Configuration

All tunable in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `DAYS_BACK` | `6` | Max age of postings to include |
| `FILTER_BY_LOCATION` | `False` | Restrict to 4 target cities only |
| `GREENHOUSE_COMPANIES` | 32 boards | Verified Greenhouse slugs |
| `ASHBY_COMPANIES` | 21 boards | Verified Ashby slugs |
| `LEVER_COMPANIES` | 2 boards | Verified Lever slugs |

## UI Features

- AG Grid table — sort/filter every column
- Quick search + source / location / role dropdowns
- Live updates via SSE — NEW badge on fresh entries
- "Scrape now" button for manual trigger
- Auto-scrapes every 60 minutes in background
