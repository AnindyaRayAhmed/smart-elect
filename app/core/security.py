import re


REFUSAL_TRIGGERS: tuple[str, ...] = (
    "who should i vote for",
    "best candidate",
    "which party is better",
    "ignore previous instructions",
    "system prompt",
)

BIAS_REPLACEMENTS: dict[str, str] = {
    "best": "notable",
    "better": "different",
    "should vote for": "can compare",
    "must vote for": "may evaluate",
    "strongly recommend": "suggest reviewing",
}


def sanitize_input(user_input: str) -> str:
    """Basic sanitization against prompt injection and malicious characters."""
    sanitized = re.sub(r"[<>|&;]", "", user_input)
    return sanitized.strip()


def _normalize_text(user_input: str) -> str:
    return " ".join(user_input.lower().strip().split())


def _contains_vote_choice_request(text: str) -> bool:
    return any(trigger in text for trigger in REFUSAL_TRIGGERS)


def _neutralize_language(text: str) -> str:
    updated_text = text
    for source, replacement in BIAS_REPLACEMENTS.items():
        updated_text = updated_text.replace(source, replacement)
        updated_text = updated_text.replace(source.capitalize(), replacement.capitalize())
    return updated_text


def apply_safety_layer(user_input: str, decision: dict[str, str | float]) -> dict[str, str | float | bool]:
    """Return a safe, neutral response structure."""
    normalized_text = _normalize_text(user_input)

    if _contains_vote_choice_request(normalized_text):
        return {
            "title": "Subjective Request Not Supported",
            "content": "I can’t recommend a candidate, but I can help you compare them fairly using our evaluation guide.",
            "next_step": "Review the candidate evaluation guide to proceed.",
            "confidence": 1.0,
            "source": "Core Safety Guidelines",
        }

    safe_decision = decision.copy()
    safe_decision["content"] = _neutralize_language(str(decision.get("content", "")))
    safe_decision["next_step"] = _neutralize_language(str(decision.get("next_step", "")))
    return safe_decision
