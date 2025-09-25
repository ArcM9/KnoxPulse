
import math
from datetime import datetime, timezone

# Simple importance scoring. You can tune weights per city.
CATEGORY_WEIGHTS = {
    "legislation": 5.0,
    "agenda": 4.0,
    "public_notice": 3.5,
    "infrastructure": 3.0,
    "safety": 3.5,
    "event": 2.0,
    "news": 2.5
}

SOURCE_TRUST = {
    "city.gov": 1.0,
    "county.gov": 0.9,
    "state.gov": 0.9,
    "us.gov": 1.0,
    "local_news": 0.6,
    "community": 0.4,
}

KEYWORD_BONUS = {
    "ordinance": 1.5,
    "zoning": 1.3,
    "budget": 1.4,
    "tax": 1.4,
    "road closure": 1.2,
    "public hearing": 1.5,
    "election": 1.6,
    "schools": 1.2,
    "water": 1.2,
    "crime": 1.2,
}

def decay_by_age(published_at):
    if not published_at:
        return 0.5
    now = datetime.now(timezone.utc)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    hours = max(1.0, (now - published_at).total_seconds() / 3600.0)
    # 50% after ~7 days (168h) -> half-life ~168h
    return 0.5 ** (hours / 168.0)

def score_item(item_dict):
    base = CATEGORY_WEIGHTS.get(item_dict.get("category","news"), 2.0)
    trust = SOURCE_TRUST.get(item_dict.get("source","community"), 0.5)
    kw_bonus = 1.0
    text = (item_dict.get("title","") + " " + (item_dict.get("summary") or "")).lower()
    for k, mult in KEYWORD_BONUS.items():
        if k in text:
            kw_bonus *= mult
    age = decay_by_age(item_dict.get("published_at"))
    is_official = 1.2 if item_dict.get("is_official") else 1.0
    return base * trust * kw_bonus * (0.7 + 0.3 * age) * is_official
