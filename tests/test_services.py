from app.core.security import apply_safety_layer, sanitize_input
from app.services.intent_router import route_user_input
from app.services.decision_engine import generate_decision

def test_sanitize_input():
    malicious = "how to vote <script>alert(1)</script>"
    clean = sanitize_input(malicious)
    assert "<" not in clean
    assert ">" not in clean

def test_intent_detection():
    routing = route_user_input("when is the election deadline")
    assert routing["intent"] == "timeline_info"
    
    routing_elig = route_user_input("can i vote if i am 17")
    assert routing_elig["intent"] == "eligibility_check"

def test_safety_layer_refusal():
    decision = {"title": "Test", "content": "Test", "next_step": "Test"}
    safe = apply_safety_layer("who should i vote for", decision)
    assert safe["title"] == "Subjective Request Not Supported"
    assert "I can’t recommend" in safe["content"]

def test_safety_layer_neutralization():
    decision = {"title": "Test", "content": "This is the best candidate.", "next_step": "You must vote for them."}
    safe = apply_safety_layer("tell me about them", decision)
    assert "notable" in safe["content"]
    assert "may evaluate" in safe["next_step"]

def test_decision_engine_structure():
    response = generate_decision("learn_process", "first_time_voter", {})
    assert "confidence" in response
    assert "source" in response
    assert response["calendar_option"] is True
