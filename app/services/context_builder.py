"""Simple context extraction for SmartElect."""

from __future__ import annotations


LOCATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Delhi": ("delhi", "new delhi"),
    "Mumbai": ("mumbai", "bombay"),
    "Bengaluru": ("bengaluru", "bangalore"),
    "Chennai": ("chennai", "madras"),
    "Kolkata": ("kolkata", "calcutta"),
    "Hyderabad": ("hyderabad",),
    "Pune": ("pune",),
    "India": ("india", "indian"),
}

URGENCY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "today": ("today", "right now", "immediately", "urgent"),
    "tomorrow": ("tomorrow", "next day"),
    "upcoming": ("upcoming", "soon", "later", "this week", "next week"),
}


def _normalize_text(user_input: str) -> str:
    return " ".join(user_input.lower().strip().split())


def _extract_location(text: str) -> str:
    for location, keywords in LOCATION_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return location
    return "unknown"


def _extract_urgency(text: str) -> str:
    for urgency, keywords in URGENCY_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return urgency
    return "general"


def build_context(user_input: str) -> dict[str, str]:
    """Return lightweight context extracted from a user's message."""
    normalized_text = _normalize_text(user_input)
    return {
        "location": _extract_location(normalized_text),
        "urgency": _extract_urgency(normalized_text),
    }
