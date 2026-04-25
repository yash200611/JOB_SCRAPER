from datetime import datetime, timedelta, timezone

# --- Date filter ---
# Summer internships are posted weeks/months in advance.
# 90 days catches everything posted since January for a summer search.
# For daily incremental use, set to 1-2.
DAYS_BACK = 90
CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)

# --- Location filter (strict — only 4 cities) ---
FILTER_BY_LOCATION = True

LOCATION_PATTERNS = {
    "NYC": ["new york", "nyc", "manhattan", "brooklyn"],
    "SF":  ["san francisco", "bay area", "palo alto", "mountain view",
             "menlo park", "sunnyvale", "san jose"],
    "London":    ["london"],
    "Singapore": ["singapore"],
}

# --- Title filters ---
TITLE_MUST_CONTAIN = ["intern"]

ROLE_KEYWORDS = [
    # SWE
    "software", "engineer", "developer", "full stack", "fullstack", "full-stack",
    "backend", "back-end", "frontend", "front-end", "platform", "infrastructure",
    "devops", "mobile", "ios", "android",
    # Data / Quant
    "data engineer", "data science", "data analyst", "machine learning",
    "ml", "ai engineer", "quant", "analytics",
    # Finance
    "investment", "analyst", "venture", "equity research",
    "asset management", "portfolio", "financial",
    # Consulting / Strategy
    "strategy", "consulting", "operations", "business analyst", "biz ops",
]

# --- Seniority / degree exclusion keywords (in title) ---
SENIOR_TITLE_KEYWORDS = [
    "senior", "staff", "lead", "principal", "director", "manager", "head of",
    "vp ", "vice president", "phd", "ph.d", "doctoral", "postdoc",
]

DEGREE_KEYWORDS = [
    "master's", "masters", "master degree", "master's degree",
    "phd", "ph.d", "doctoral", "graduate degree",
    "mba", "ms degree", "m.s.", "pursuing a master",
]

# Known experience-level phrases to reject (in description snippets)
EXPERIENCE_KEYWORDS = [
    "3+ years", "4+ years", "5+ years", "3 years of experience",
    "4 years of experience", "5 years of experience",
]

# --- Blocklist (case-insensitive substring match on company name) ---
BLOCKED_COMPANIES = [
    # User-specified big startups
    "stripe", "anduril", "anthropic", "openai", "databricks", "scale ai", "scaleai",
    "figma", "notion", "rippling", "plaid", "ramp", "brex",
    # Big tech
    "google", "meta", "apple", "amazon", "microsoft", "netflix", "nvidia",
    "oracle", "salesforce", "adobe", "ibm", "cisco", "intel", "samsung",
    "uber", "lyft", "twitter", "x corp",
    # Finance
    "goldman sachs", "jpmorgan", "morgan stanley", "citi", "bank of america",
    "barclays", "hsbc", "ubs", "credit suisse", "deutsche bank", "bnp paribas",
    "lazard", "evercore", "moelis", "pjt", "centerview", "jefferies",
    "houlihan lokey", "william blair", "nomura", "macquarie",
    # Consulting / Big 4
    "mckinsey", "bcg", "bain", "deloitte", "pwc", "kpmg", "ernst & young",
    "accenture", "booz allen", "oliver wyman",
    # PE / mega VC
    "kkr", "blackstone", "carlyle", "apollo", "tpg", "warburg pincus",
    "andreessen horowitz", "a16z", "sequoia", "kleiner perkins",
    # Large public fintech / crypto
    "robinhood", "coinbase",
    # Other large companies that leaked in
    "airtable", "databricks", "flexport",
]

# --- Known company stages (best-effort) ---
COMPANY_STAGES = {
    # Series A/B
    "mercury": "Series B", "pave": "Series B", "vanta": "Series C",
    "livekit": "Series B", "neon": "Series B", "goldsky": "Series A",
    "freshpaint": "Series B", "prefect": "Series B", "mux": "Series C",
    # Series C/D
    "deepgram": "Series C", "assemblyai": "Series C", "airbyte": "Series C",
    "retool": "Series C", "posthog": "Series C", "sentry": "Series F",
    "linear": "Series B", "cursor": "Series B", "runway": "Series C",
    "phantom": "Series A", "alchemy": "Series C", "bolt": "Series D",
    "modal": "Series B", "cohere": "Series D", "mistral": "Series B",
    "replit": "Series B", "snyk": "Series G", "launchdarkly": "Series D",
    "temporal": "Series B", "cockroachlabs": "Series F", "planetscale": "Series C",
    "labelbox": "Series D", "warp": "Series B", "vercel": "Series E",
    "supabase": "Series C", "pave": "Series B", "nerdwallet": "Public",
    "wealthfront": "Acquired", "anchorage": "Series D",
    "gusto": "Series E", "carta": "Series G", "faire": "Series H",
    "perplexity": "Series C", "elevenlabs": "Series C",
    "clarifai": "Series C", "postman": "Series D",
}

# --- Greenhouse company boards (verified slugs, big companies removed) ---
GREENHOUSE_COMPANIES = [
    "mercury", "postman", "launchdarkly", "cockroachlabs", "temporal",
    "assemblyai", "labelbox", "clarifai", "planetscale", "vercel", "warp",
    "gusto", "faire", "carta",
]

# --- Lever company boards (verified slugs) ---
LEVER_COMPANIES = [
    "wealthfront",
    "anchorage",
]

# --- Ashby company boards (verified slugs, big companies removed) ---
ASHBY_COMPANIES = [
    "perplexity", "cohere", "mistral", "replit", "linear", "vanta",
    "pave", "modal", "elevenlabs", "runway", "deepgram", "mux", "airbyte",
    "prefect", "phantom", "alchemy", "goldsky", "bolt", "freshpaint",
    "supabase", "snyk", "neon", "posthog", "sentry", "cursor", "retool",
    "livekit", "nerdwallet",
]

# --- HTTP settings ---
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_BACKOFF = 2
