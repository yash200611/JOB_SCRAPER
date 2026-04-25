import re
from config import LOCATION_PATTERNS, TITLE_MUST_CONTAIN, ROLE_KEYWORDS, BLOCKED_COMPANIES, FILTER_BY_LOCATION


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text)


def match_location(location_text: str) -> str | None:
    """Return canonical city name if known, else the raw location or None.

    When FILTER_BY_LOCATION is False, unknown locations are passed through as-is
    so no jobs are dropped on location. Returns None only for empty input.
    """
    if not location_text or not location_text.strip():
        return None if FILTER_BY_LOCATION else "Unknown"

    loc = location_text.lower()
    for city, patterns in LOCATION_PATTERNS.items():
        for pat in patterns:
            if pat in loc:
                return city

    # No pattern matched
    if FILTER_BY_LOCATION:
        return None
    # Return cleaned raw text (truncated for readability)
    raw = location_text.strip()
    return raw[:50] if raw else "Unknown"


def match_title(title: str) -> bool:
    """Return True if title matches intern filter AND at least one role keyword."""
    t = title.lower()
    has_intern = any(kw in t for kw in TITLE_MUST_CONTAIN)
    has_role = any(kw in t for kw in ROLE_KEYWORDS)
    return has_intern and has_role


def is_blocked(company_name: str) -> bool:
    c = company_name.lower()
    return any(blocked in c for blocked in BLOCKED_COMPANIES)
