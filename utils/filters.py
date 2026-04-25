import re
from config import (
    LOCATION_PATTERNS, TITLE_MUST_CONTAIN, ROLE_KEYWORDS, BLOCKED_COMPANIES,
    FILTER_BY_LOCATION, SENIOR_TITLE_KEYWORDS, DEGREE_KEYWORDS, EXPERIENCE_KEYWORDS,
)


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text)


def match_location(location_text: str) -> str | None:
    """Return canonical city or None.

    When FILTER_BY_LOCATION=True, returns None for unrecognized locations.
    When False, returns raw location string as fallback.
    """
    if not location_text or not location_text.strip():
        return None if FILTER_BY_LOCATION else "Unknown"

    loc = location_text.lower()
    for city, patterns in LOCATION_PATTERNS.items():
        for pat in patterns:
            if pat in loc:
                return city

    if FILTER_BY_LOCATION:
        return None
    raw = location_text.strip()
    return raw[:50] if raw else "Unknown"


def match_title(title: str) -> bool:
    """Must contain 'intern' AND at least one role keyword."""
    t = title.lower()
    has_intern = any(kw in t for kw in TITLE_MUST_CONTAIN)
    has_role = any(kw in t for kw in ROLE_KEYWORDS)
    return has_intern and has_role


def is_blocked(company_name: str) -> bool:
    c = company_name.lower()
    return any(blocked in c for blocked in BLOCKED_COMPANIES)


def is_senior_role(title: str) -> bool:
    """True if title signals a senior/staff/PhD level role."""
    t = title.lower()
    return any(kw in t for kw in SENIOR_TITLE_KEYWORDS)


def requires_advanced_degree(title: str, description: str = "") -> bool:
    """True if job requires Master's, PhD, or 3+ years experience."""
    combined = (title + " " + description).lower()
    for kw in DEGREE_KEYWORDS:
        if kw in combined:
            return True
    for kw in EXPERIENCE_KEYWORDS:
        if kw in combined:
            return True
    return False


def is_eligible(title: str, description: str = "") -> bool:
    """Combined eligibility check: intern-level, right role, no advanced degree."""
    if not match_title(title):
        return False
    if is_senior_role(title):
        return False
    if requires_advanced_degree(title, description):
        return False
    return True


# --- Role categorization ---
ROLE_CATEGORIES = {
    "SWE": [
        "software", "engineer", "developer", "full stack", "fullstack", "full-stack",
        "backend", "frontend", "platform", "infrastructure", "devops", "mobile",
        "ios", "android", "site reliability",
    ],
    "Data/Quant": [
        "data engineer", "data science", "data analyst", "machine learning",
        "ml engineer", "ai engineer", "quant", "analytics",
    ],
    "Finance": [
        "investment", "venture capital", "vc analyst", "equity research",
        "asset management", "portfolio", "financial analyst",
    ],
    "Consulting": ["strategy", "consulting", "operations", "business analyst", "biz ops"],
}


def categorize_role(title: str) -> str:
    t = title.lower()
    for cat, keywords in ROLE_CATEGORIES.items():
        if any(kw in t for kw in keywords):
            return cat
    return "Other"
