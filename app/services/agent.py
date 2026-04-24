"""Main orchestration flow for SmartElect."""

from __future__ import annotations
from typing import Any

from app.core.security import apply_safety_layer, sanitize_input
from app.services.context_builder import build_context
from app.services.decision_engine import generate_decision
from app.services.google_calendar import generate_ics_event
from app.services.intent_router import route_user_input, INTENT_KEYWORDS, _detect_persona
from app.services.llm_service import LLMService


def process_user_input(raw_user_input: str, mode: str = "guided") -> dict[str, Any]:
    """Run the full SmartElect rule-based pipeline for one message."""
    user_input = sanitize_input(raw_user_input)

    routing = route_user_input(user_input)
    intent = routing["intent"]
    persona = routing["persona"]

    if intent == "out_of_scope":
        allowed_intents = list(INTENT_KEYWORDS.keys())
        assisted_intent = LLMService.assist_intent(user_input, allowed_intents)
        if assisted_intent and assisted_intent != "out_of_scope":
            intent = assisted_intent
            persona = _detect_persona(user_input, intent)

    context = build_context(user_input)
    decision = generate_decision(intent=intent, persona=persona, context=context, user_input=user_input, mode=mode)
    
    if mode == "guided":
        polished = LLMService.polish_response(
            decision_content=str(decision.get("content", "")),
            decision_next_step=str(decision.get("next_step", "")),
            user_input=user_input
        )
        decision["content"] = polished["content"]
        decision["next_step"] = polished["next_step"]

    safe_decision = apply_safety_layer(user_input, decision)

    response: dict[str, Any] = {
        "intent": intent,
        "persona": persona,
        "response": safe_decision["content"],
        "title": safe_decision["title"],
        "next_step": safe_decision["next_step"],
        "confidence": safe_decision.get("confidence", 0.8),
        "source": safe_decision.get("source", "SmartElect Default"),
    }

    if bool(safe_decision.get("calendar_option")):
        response["calendar_option"] = True
        response["event_title"] = safe_decision.get("event_title", "")
        response["event_description"] = safe_decision.get("event_description", "")
        response["event_date"] = safe_decision.get("event_date", "2026-01-01")
        response["calendar_event"] = generate_ics_event(
            title=str(response["event_title"]),
            description=str(response["event_description"]),
            date=str(response["event_date"]),
            event_type=str(safe_decision.get("event_type", "general")),
        )

    return response
