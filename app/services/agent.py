"""Main orchestration flow for SmartElect."""

from __future__ import annotations
from typing import Any
import uuid

from app.core.security import apply_safety_layer, sanitize_input
from app.services.context_builder import build_context
from app.services.decision_engine import generate_decision
from app.services.google_calendar import generate_ics_event
from app.services.intent_router import route_user_input, INTENT_KEYWORDS, _detect_persona
from app.services.llm_service import LLMService

_SESSION_STORE: dict[str, dict[str, Any]] = {}

def process_user_input(raw_user_input: str, mode: str = "guided", session_id: str | None = None) -> dict[str, Any]:
    """Run the full SmartElect pipeline for one message."""
    user_input = sanitize_input(raw_user_input)
    
    if not session_id:
        session_id = str(uuid.uuid4())
        
    if session_id not in _SESSION_STORE:
        _SESSION_STORE[session_id] = {}
        
    session_context = _SESSION_STORE[session_id]

    if mode == "explore":
        llm_response = LLMService.generate_explore_response(user_input)
        if not llm_response:
            llm_response = "The system is temporarily unable to generate a response. Please try again."
        
        return {
            "intent": "explore",
            "persona": "general",
            "response": llm_response,
            "title": "Conversational Assistant",
            "next_step": "Ask any other civic questions.",
            "confidence": 0.9,
            "source": "LLM Generated",
            "session_id": session_id
        }

    # Guided Mode
    interpretation = LLMService.interpret_user_input(user_input)
    
    # Merge extracted entities into session context
    for key, value in interpretation.get("entities", {}).items():
        if value is not None:
            session_context[key] = value
            
    # Also build basic rule-based context and merge
    base_context = build_context(user_input)
    for k, v in base_context.items():
        if k not in session_context or session_context[k] == "unknown":
            session_context[k] = v

    # Intent resolution
    llm_intent = interpretation.get("intent")
    routing = route_user_input(user_input)
    
    intent = llm_intent if llm_intent else routing["intent"]
    persona = routing["persona"]
    
    if intent not in INTENT_KEYWORDS and intent != "out_of_scope":
        intent = routing["intent"]

    decision = generate_decision(intent=intent, persona=persona, context=session_context, user_input=user_input, mode=mode)
    safe_decision = apply_safety_layer(user_input, decision)

    response: dict[str, Any] = {
        "intent": intent,
        "persona": persona,
        "response": safe_decision["content"],
        "title": safe_decision["title"],
        "next_step": safe_decision["next_step"],
        "confidence": safe_decision.get("confidence", 0.8),
        "source": safe_decision.get("source", "SmartElect Default"),
        "is_verified": safe_decision.get("is_verified", False),
        "session_id": session_id
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
