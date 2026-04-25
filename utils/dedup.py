import re
from typing import List, Dict

SOURCE_PRIORITY = {
    "greenhouse": 0,
    "lever": 1,
    "ashby": 2,
    "yc": 3,
    "wellfound": 4,
    "hackernews": 5,
}


def _dedup_key(job: Dict) -> str:
    def norm(s: str) -> str:
        s = s.lower().strip()
        s = re.sub(r"[^\w]", "", s)
        return s

    return norm(job.get("company_name", "")) + "|" + norm(job.get("role_title", "")) + "|" + norm(job.get("location", ""))


def deduplicate(jobs: List[Dict]) -> List[Dict]:
    seen: Dict[str, Dict] = {}
    for job in jobs:
        key = _dedup_key(job)
        if key not in seen:
            seen[key] = job
        else:
            existing_priority = SOURCE_PRIORITY.get(seen[key].get("source", ""), 99)
            new_priority = SOURCE_PRIORITY.get(job.get("source", ""), 99)
            if new_priority < existing_priority:
                seen[key] = job
    return list(seen.values())
