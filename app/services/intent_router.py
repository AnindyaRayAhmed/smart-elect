"""Rule-based routing for user intent and persona."""

from __future__ import annotations


INTENT_KEYWORDS: dict[str, tuple[str, ...]] = {
    "learn_process": (
        "how to vote",
        "voting process",
        "election process",
        "how do i vote",
        "how can i vote",
        "steps to vote",
        "first time voting",
        "first-time voting",
        "i have never voted before",
    ),
    "eligibility_check": (
        "am i eligible",
        "eligible to vote",
        "eligibility",
        "can i vote",
        "who can vote",
        "minimum age",
    ),
    "timeline_info": (
        "last date",
        "deadline",
        "timeline",
        "when is election",
        "when can i register",
        "schedule",
        "important dates",
    ),
    "booth_lookup": (
        "polling booth",
        "booth",
        "polling station",
        "where do i vote",
        "voting location",
        "electoral search",
    ),
    "candidate_compare": (
        "compare candidates",
        "candidate comparison",
        "candidate compare",
        "compare manifesto",
        "candidate details",
        "compare parties",
        "who should i vote for",
    ),
    "registration_help": (
        "register to vote",
        "voter registration",
        "how to register",
        "register myself",
        "new voter",
        "apply for voter id",
        "enroll as voter",
    ),
    "document_requirements": (
        "documents required",
        "required documents",
        "what documents",
        "id proof",
        "address proof",
        "documents for voter id",
    ),
    "election_day_preparation": (
        "election day",
        "what to do on voting day",
        "how to prepare",
        "before voting",
        "what should i carry",
        "voting day checklist",
    ),
    "faq": (
        "faq",
        "frequently asked questions",
        "common questions",
        "help me understand",
        "i have a question",
    ),
}


PERSONA_KEYWORDS: dict[str, tuple[str, ...]] = {
    "first_time_voter": (
        "first time",
        "new voter",
        "never voted",
        "i have never voted before",
        "first time voting",
        "how do i vote",
        "my first vote",
        "first-time voter",
    ),
    "returning_voter": (
        "voted before",
        "returning voter",
        "already registered",
        "my old voter id",
        "update my voter id",
    ),
    "informed_voter": (
        "compare candidates",
        "manifesto",
        "issues",
        "policy",
        "research candidates",
    ),
    "researcher": (
        "research",
        "data",
        "statistics",
        "study",
        "analyze",
        "analysis",
    ),
    "confused_user": (
        "confused",
        "not sure",
        "don't understand",
        "do not understand",
        "help",
        "what do i do",
    ),
}


def _normalize_text(user_input: str) -> str:
    return " ".join(user_input.lower().strip().split())


def _detect_intent(text: str) -> str:
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return intent
    return "out_of_scope"


def _detect_persona(text: str, intent: str) -> str:
    for persona, keywords in PERSONA_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return persona

    if intent == "learn_process":
        return "first_time_voter"
    if intent in {"registration_help", "document_requirements", "eligibility_check"}:
        return "confused_user"
    if intent == "candidate_compare":
        return "informed_voter"

    return "returning_voter"


def route_user_input(user_input: str) -> dict[str, str]:
    """Return the detected intent and persona for a user's message."""
    normalized_text = _normalize_text(user_input)
    intent = _detect_intent(normalized_text)
    persona = _detect_persona(normalized_text, intent)
    return {
        "intent": intent,
        "persona": persona,
    }
