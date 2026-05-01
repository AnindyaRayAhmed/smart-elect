import pytest
import json
import logging
import time
from unittest.mock import patch, MagicMock

from app.services.agent import process_user_input
from app.services.intent_router import INTENT_KEYWORDS
from app.core.security import sanitize_input
from app.services.llm_service import LLMService, _intent_cache, _normalize_cache_key


# -- Mock Behaviors for LLMService --
def mock_llm_guided(mock_intent, mock_entities=None, mock_confidence=0.9):
    def _mock(prompt):
        return json.dumps({
            "intent": mock_intent,
            "entities": mock_entities or {},
            "confidence": mock_confidence
        })
    return _mock


def mock_llm_explore(mock_text):
    def _mock(prompt):
        return mock_text
    return _mock


@pytest.fixture
def mock_firestore():
    with patch("app.services.agent.log_interaction") as mock_log:
        yield mock_log


@pytest.fixture(autouse=True)
def clear_intent_cache():
    """Clear the intent cache before each test to ensure isolation."""
    _intent_cache.clear()
    # Reset client singletons so mocks work cleanly
    LLMService._gemini_client = None
    LLMService._openai_client = None
    yield
    _intent_cache.clear()
    LLMService._gemini_client = None
    LLMService._openai_client = None


class TestIntentInterpretation:
    """Tests for intent extraction and routing."""
    
    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_intent_learn_process(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("learn_process")
        res = process_user_input("how do I vote for the first time")
        
        assert res["intent"] == "learn_process"
        assert res["title"] == "Guide: First-Time Voter"
        assert res["calendar_option"] is True

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_intent_eligibility(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("eligibility_check")
        res = process_user_input("am i eligible to vote")
        
        assert res["intent"] == "eligibility_check"
        assert "Eligibility" in res["title"]

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_intent_out_of_scope(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("out_of_scope")
        res = process_user_input("how to bake a cake")
        
        assert res["intent"] == "out_of_scope"
        assert res["title"] == "Outside Supported Topics"

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_intent_fallback_bad_json(self, mock_gen, mock_firestore):
        # Return invalid JSON
        mock_gen.return_value = "This is not JSON"
        # Since rule-based router will catch "how to vote", it should route to learn_process
        res = process_user_input("how to vote")
        
        assert res["intent"] == "learn_process"


class TestEntityExtraction:
    """Tests for entity extraction and session state building."""

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_entity_all_missing(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("eligibility_check", {"age": None, "citizenship": None, "location": None})
        res = process_user_input("am I eligible", session_id="sess_1")
        
        assert res["is_verified"] is False
        assert "Additional Information Required" in res["title"]
        assert "Age" in res["response"]
        assert "Citizenship status" in res["response"]
        assert "Location" in res["response"]

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_entity_partial_extracted(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("eligibility_check", {"age": 25})
        res = process_user_input("I am 25 years old", session_id="sess_2")
        
        assert res["is_verified"] is False
        assert "Citizenship status" in res["response"]
        assert "Age: 25" in res["response"]

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_entity_all_extracted_verified(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("eligibility_check", {"age": 30, "citizenship": "indian", "location": "Delhi"})
        res = process_user_input("I am 30, indian, living in Delhi", session_id="sess_3")
        
        assert res["is_verified"] is True
        assert res["title"] == "Eligibility Verified"

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_entity_session_memory(self, mock_gen, mock_firestore):
        sess_id = "mem_sess_1"
        # Turn 1: Provide Age
        mock_gen.side_effect = mock_llm_guided("eligibility_check", {"age": 25})
        process_user_input("I am 25", session_id=sess_id)
        
        # Turn 2: Provide Citizenship
        mock_gen.side_effect = mock_llm_guided("eligibility_check", {"citizenship": "indian"})
        process_user_input("I am indian", session_id=sess_id)
        
        # Turn 3: Provide Location
        mock_gen.side_effect = mock_llm_guided("eligibility_check", {"location": "Mumbai"})
        res = process_user_input("I live in Mumbai", session_id=sess_id)
        
        assert res["is_verified"] is True
        assert res["title"] == "Eligibility Verified"


class TestDecisionEngineOutputs:
    """Tests for deterministic outputs of the decision engine."""

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_decision_timeline_info(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("timeline_info")
        res = process_user_input("when is the deadline")
        assert res["title"] == "Official Electoral Timelines"
        assert res["calendar_option"] is True

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_decision_booth_lookup(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("booth_lookup")
        res = process_user_input("where is my booth")
        assert res["title"] == "Polling Station Locator"

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_decision_registration_help(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("registration_help")
        res = process_user_input("how to register")
        assert res["title"] == "Registration Guide"

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_decision_candidate_compare(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("candidate_compare")
        res = process_user_input("compare candidates")
        assert res["title"] == "Candidate Evaluation Guide"

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_decision_election_day(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("election_day_preparation")
        res = process_user_input("election day")
        assert res["title"] == "Election Day Steps"
        assert res["calendar_option"] is True


class TestExploreMode:
    """Tests for the Explore Mode generative conversational flow."""

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_explore_mode_success(self, mock_gen, mock_firestore):
        llm_response = "Here is a conversational explanation of voting like a pizza slice..."
        mock_gen.side_effect = mock_llm_explore(llm_response)
        
        res = process_user_input("Explain voting to me", mode="explore")
        assert res["intent"] == "explore"
        assert res["response"] == llm_response

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_explore_mode_llm_failure(self, mock_gen, mock_firestore):
        mock_gen.return_value = None
        
        res = process_user_input("Explain voting", mode="explore")
        assert res["intent"] == "explore"
        assert "unable to generate a response" in res["response"]


class TestEdgeCases:
    """Tests for system edge cases like malicious input and empty strings."""

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_edge_case_html_injection(self, mock_gen, mock_firestore):
        # We don't care about LLM output here, just that it doesn't break
        mock_gen.side_effect = mock_llm_guided("out_of_scope")
        malicious_input = "<script>alert(1)</script> hello"
        
        sanitized = sanitize_input(malicious_input)
        assert "<" not in sanitized
        assert ">" not in sanitized
        
        res = process_user_input(malicious_input)
        assert res is not None

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_edge_case_empty_input(self, mock_gen, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("out_of_scope")
        res = process_user_input("   ")
        # An empty string likely falls out of scope
        assert res["intent"] == "out_of_scope"


class TestStructuredLogging:
    """Test to validate structured logging output format."""

    @patch("app.core.logger.logger.info")
    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_structured_logging_format(self, mock_gen, mock_logger_info, mock_firestore):
        mock_gen.side_effect = mock_llm_guided("learn_process")
        
        process_user_input("how to vote", session_id="log_sess_1")
        
        assert mock_logger_info.call_count > 0
        
        # Check the payload passed to the logger
        for call_args in mock_logger_info.call_args_list:
            args, kwargs = call_args
            extra = kwargs.get("extra")
            assert extra is not None
            
            payload = extra.get("gcl_payload")
            assert payload is not None
            
            # Assert schema keys
            assert "request_id" in payload
            assert "session_id" in payload
            assert "timestamp" in payload
            assert "stage" in payload
            assert "component" in payload
            assert "latency_ms" in payload
            
            # Additional keys that should be in payload
            assert "input" in payload
            assert "intent" in payload
            assert "status" in payload
            
            # Timestamp should be an ISO formatted string
            assert isinstance(payload["timestamp"], str)
            assert "T" in payload["timestamp"]
            
            # Verify latency is an int
            assert isinstance(payload["latency_ms"], int)


class TestPerformanceOptimizations:
    """Tests for caching, client reuse, and routing efficiency."""

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_cache_hit_avoids_duplicate_llm_call(self, mock_gen, mock_firestore):
        """Two identical inputs should trigger only ONE _generate_completion call."""
        mock_gen.side_effect = mock_llm_guided("learn_process")

        res1 = process_user_input("how do I vote for the first time")
        res2 = process_user_input("how do I vote for the first time")

        # LLM called exactly once (second was cache hit)
        assert mock_gen.call_count == 1
        # Both responses identical
        assert res1["intent"] == res2["intent"] == "learn_process"

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_cache_miss_on_different_inputs(self, mock_gen, mock_firestore):
        """Two distinct inputs should each trigger a separate LLM call."""
        mock_gen.side_effect = [
            json.dumps({"intent": "learn_process", "entities": {}, "confidence": 0.9}),
            json.dumps({"intent": "eligibility_check", "entities": {}, "confidence": 0.9}),
        ]

        res1 = process_user_input("how do I vote")
        res2 = process_user_input("am I eligible to vote")

        assert mock_gen.call_count == 2
        assert res1["intent"] == "learn_process"
        assert res2["intent"] == "eligibility_check"

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_cache_ttl_expiry(self, mock_gen, mock_firestore):
        """Cached entry should expire after TTL and trigger a fresh LLM call."""
        mock_gen.side_effect = mock_llm_guided("learn_process")

        # First call — cache miss
        process_user_input("how do I vote")
        assert mock_gen.call_count == 1

        # Manually expire the cache entry by backdating its timestamp
        normalized = _normalize_cache_key("how do I vote")
        _intent_cache._timestamps[normalized] = time.monotonic() - (_intent_cache._ttl + 1)

        # Second call — should be a fresh LLM call after expiry
        process_user_input("how do I vote")
        assert mock_gen.call_count == 2

    def test_client_singleton_returns_same_object(self):
        """_get_gemini_client should return the same instance on repeated calls."""
        mock_client = MagicMock()
        LLMService._gemini_client = mock_client

        client1 = LLMService._get_gemini_client()
        client2 = LLMService._get_gemini_client()

        assert client1 is client2
        assert client1 is mock_client

    @patch("app.services.llm_service.LLMService._generate_completion")
    def test_high_confidence_uses_llm_intent(self, mock_gen, mock_firestore):
        """When LLM returns high confidence, its intent should be used directly."""
        mock_gen.side_effect = mock_llm_guided("registration_help", mock_confidence=0.95)

        res = process_user_input("I need to register to vote")

        assert res["intent"] == "registration_help"
        assert res["title"] == "Registration Guide"
