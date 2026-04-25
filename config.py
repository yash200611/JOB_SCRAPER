from datetime import datetime, timedelta, timezone

# --- Date filter ---
DAYS_BACK = 6
CUTOFF_DATE = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)

# --- Location matching ---
# Any job is accepted; we normalize the location to a canonical city name if we can
# otherwise we keep the raw location string. Set FILTER_BY_LOCATION = True to
# restrict to the four target cities only.
FILTER_BY_LOCATION = False

LOCATION_PATTERNS = {
    "NYC": ["new york", "nyc", "manhattan", "brooklyn", " ny,", " ny "],
    "SF": [
        "san francisco", " sf,", " sf ", "bay area", "palo alto",
        "mountain view", "menlo park", "sunnyvale", "san jose", "oakland", "berkeley",
    ],
    "London": ["london", " uk,", " uk ", "united kingdom"],
    "Singapore": ["singapore", " sg,", " sg "],
    "Remote": ["remote", "anywhere", "distributed", "worldwide"],
    "Seattle": ["seattle", " wa,", " wa "],
    "Boston": ["boston", "cambridge, ma"],
    "Austin": ["austin", " tx,"],
    "Chicago": ["chicago"],
    "LA": ["los angeles", " la,", "santa monica", "culver city"],
    "Denver": ["denver", "colorado"],
    "Miami": ["miami"],
    "Toronto": ["toronto", "canada"],
    "Berlin": ["berlin"],
    "Amsterdam": ["amsterdam"],
    "Paris": ["paris"],
    "Zurich": ["zurich", "zürich"],
    "Dubai": ["dubai"],
    "Sydney": ["sydney"],
    "Tokyo": ["tokyo"],
    "Bangalore": ["bangalore", "bengaluru"],
}

# --- Title filters ---
TITLE_MUST_CONTAIN = ["intern"]

ROLE_KEYWORDS = [
    # SWE
    "software", "full stack", "fullstack", "full-stack", "backend", "back-end",
    "frontend", "front-end", "platform", "infrastructure", "devops", "site reliability",
    "mobile", "ios", "android", "web developer", "product engineer",
    # Data / Quant
    "data engineer", "data science", "data analyst", "quantitative", "quant",
    "machine learning", "ml engineer", "ai engineer", "analytics",
    # Finance
    "venture capital", "vc analyst", "investment", "equity research",
    "asset management", "portfolio", "financial analyst", "deal",
    # Consulting / Strategy
    "strategy", "consulting", "operations", "business analyst", "biz ops",
]

# --- Blocklist ---
BLOCKED_COMPANIES = [
    "google", "meta", "apple", "amazon", "microsoft", "netflix", "nvidia", "oracle",
    "salesforce", "adobe", "ibm", "cisco", "intel", "samsung", "uber", "lyft",
    "goldman sachs", "jpmorgan", "morgan stanley", "citi", "bank of america",
    "barclays", "hsbc", "ubs", "credit suisse", "deutsche bank", "bnp paribas",
    "lazard", "evercore", "moelis", "pjt", "centerview", "jefferies",
    "houlihan lokey", "william blair", "nomura", "macquarie",
    "mckinsey", "bcg", "bain", "deloitte", "pwc", "kpmg", "ey ", "ernst & young",
    "accenture", "booz allen", "oliver wyman",
    "kkr", "blackstone", "carlyle", "apollo", "tpg", "warburg pincus",
    "andreessen horowitz", "a16z", "sequoia", "kleiner perkins",
]

# --- Greenhouse company boards (verified slugs) ---
GREENHOUSE_COMPANIES = [
    # Core tech startups
    "stripe", "brex", "figma", "airtable", "databricks", "anthropic", "vercel",
    "mercury", "postman", "launchdarkly", "cockroachlabs", "temporal",
    "assemblyai", "labelbox", "clarifai", "planetscale",
    # Correct slugs discovered via API probe
    "scaleai",          # Scale AI
    "andurilindustries", # Anduril
    "robinhood",
    "coinbase",
    "carta",
    "gusto",
    "faire",
    "flexport",
]

# --- Lever company boards (verified slugs) ---
LEVER_COMPANIES = [
    "wealthfront",
    "anchorage",  # Anchorage Digital
]

# --- Ashby company boards (verified slugs) ---
ASHBY_COMPANIES = [
    # Original
    "notion", "ramp", "perplexity",
    # Discovered via API probe
    "nerdwallet", "openai", "cohere", "mistral", "replit", "linear", "vanta",
    "pave", "modal", "plaid",
    "elevenlabs", "runway", "deepgram", "mux", "airbyte", "prefect",
    "phantom", "alchemy", "goldsky", "bolt",
]

# --- HTTP settings ---
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, doubles each retry
