"""LLM Service for SmartElect intent assistance and response polishing."""

import json
import logging
import os
import time
from functools import lru_cache
from typing import Optional, Any

logger = logging.getLogger(__name__)

# System flag to enable/disable LLM globally
LLM_ENABLED = os.getenv("LLM_ENABLED", "True").lower() in ("true", "1", "yes")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()

# Cache configuration (tunable via environment)
_CACHE_MAX_SIZE = int(os.getenv("LLM_CACHE_MAX_SIZE", "128"))
_CACHE_TTL_SECONDS = int(os.getenv("LLM_CACHE_TTL", "300"))


def _normalize_cache_key(text: str) -> str:
    """Normalize input for consistent cache key generation."""
    return " ".join(text.lower().strip().split())


class _IntentCache:
    """TTL-bounded LRU cache for intent interpretation results.

    Wraps functools.lru_cache with a per-entry timestamp so stale
    entries are transparently refreshed after ``_CACHE_TTL_SECONDS``.
    """

    def __init__(self, maxsize: int = _CACHE_MAX_SIZE, ttl: int = _CACHE_TTL_SECONDS):
        self._ttl = ttl
        self._timestamps: dict[str, float] = {}

        @lru_cache(maxsize=maxsize)
        def _cached_interpret(normalized_input: str) -> str:
            """Returns a JSON-encoded string (hashable for lru_cache)."""
            # Actual LLM call is delegated back to LLMService
            result = LLMService._interpret_user_input_uncached(normalized_input)
            self._timestamps[normalized_input] = time.monotonic()
            return json.dumps(result)

        self._cached_fn = _cached_interpret

    def get(self, normalized_input: str) -> Optional[dict[str, Any]]:
        """Return cached result if fresh, or None to signal a miss."""
        cached_time = self._timestamps.get(normalized_input)
        if cached_time is not None and (time.monotonic() - cached_time) > self._ttl:
            # Evict stale entry
            self._timestamps.pop(normalized_input, None)
            self._cached_fn.cache_clear()
            return None

        try:
            raw = self._cached_fn(normalized_input)
            return json.loads(raw)
        except Exception:
            return None

    def clear(self) -> None:
        """Clear all cached entries (useful for testing)."""
        self._cached_fn.cache_clear()
        self._timestamps.clear()


# Module-level singleton cache instance
_intent_cache = _IntentCache()


class LLMService:
    """Abstract service for safe, thin-layer LLM integration."""

    # -- Client singletons (one per process lifetime) --
    _gemini_client: Any = None
    _openai_client: Any = None

    @classmethod
    def _get_gemini_client(cls) -> Any:
        """Lazily initialize and return a reusable Gemini client."""
        if cls._gemini_client is None:
            from google import genai

            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.error("GOOGLE_API_KEY missing")
                return None
            cls._gemini_client = genai.Client(api_key=api_key)
        return cls._gemini_client

    @classmethod
    def _get_openai_client(cls) -> Any:
        """Lazily initialize and return a reusable OpenAI client."""
        if cls._openai_client is None:
            import openai
            cls._openai_client = openai.OpenAI()
        return cls._openai_client

    @classmethod
    def _generate_completion(cls, prompt: str) -> Optional[str]:
        """Wrapper to call the configured LLM provider."""
        if not LLM_ENABLED:
            return None

        try:
            if LLM_PROVIDER == "gemini":
                client = cls._get_gemini_client()
                if client is None:
                    return None

                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt
                )
                logger.info("LLM CALL SUCCESS")
                # Primary path
                if hasattr(response, "text") and response.text:
                    return response.text.strip()
                # Fallback for Gemini 2.5 response structure
                try:
                    return response.candidates[0].content.parts[0].text.strip()
                except Exception:
                    logger.error("LLM RESPONSE PARSING FAILED")
                    return None
            elif LLM_PROVIDER == "openai":
                client = cls._get_openai_client()
                if client is None:
                    return None
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                logger.info("LLM CALL SUCCESS")
                return response.choices[0].message.content.strip() if response.choices else None
            else:
                logger.warning(f"Unknown LLM provider: {LLM_PROVIDER}")
                return None
        except Exception as e:
            logger.error(f"LLM FAILED: {str(e)}")
            return None

    @classmethod
    def _interpret_user_input_uncached(cls, normalized_input: str) -> dict[str, Any]:
        """Core interpretation logic — called on cache miss only."""
        prompt = (
            "You are a routing and extraction assistant for a deterministic civic platform in India.\n"
            "Analyze the following user input and extract the intent and entities.\n"
            "Valid intents are: 'learn_process', 'eligibility_check', 'timeline_info', "
            "'booth_lookup', 'candidate_compare', 'registration_help', "
            "'document_requirements', 'election_day_preparation', 'faq'.\n"
            "If the intent is unclear or does not match these, output null for intent.\n"
            "Extract these entities if present: 'age' (number), 'citizenship' ('indian' or 'non-indian'), 'location' (string).\n"
            "If an entity is not present, output null for it.\n"
            "NEVER hallucinate missing values.\n\n"
            "OUTPUT FORMAT MUST BE EXACTLY THIS JSON (no other text or markdown tags):\n"
            "{\n"
            '  "intent": "...",\n'
            '  "entities": {\n'
            '    "age": null,\n'
            '    "citizenship": null,\n'
            '    "location": null\n'
            "  },\n"
            '  "confidence": 0.0\n'
            "}\n\n"
            f"User input: \"{normalized_input}\""
        )

        response_text = cls._generate_completion(prompt)

        if not response_text:
            return {"intent": None, "entities": {}, "confidence": 0.0}

        try:
            # Strip markdown formatting if the LLM adds it
            clean_json = response_text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(clean_json)
            logger.info("LLM_INTERPRET_USED")
            return {
                "intent": parsed.get("intent"),
                "entities": parsed.get("entities", {}),
                "confidence": parsed.get("confidence", 0.0)
            }
        except Exception as e:
            logger.error(f"LLM JSON PARSING FAILED: {str(e)}")
            return {"intent": None, "entities": {}, "confidence": 0.0}

    @classmethod
    def interpret_user_input(cls, user_input: str) -> dict[str, Any]:
        """Extract intent and entities from user input, returning strict JSON.

        Results are cached by normalized input text to avoid redundant LLM
        calls for repeated queries within the cache TTL window.
        """
        if not LLM_ENABLED:
            return {"intent": None, "entities": {}, "confidence": 0.0}

        normalized = _normalize_cache_key(user_input)
        cached_result = _intent_cache.get(normalized)

        if cached_result is not None:
            logger.info("LLM_INTERPRET_CACHE_HIT")
            return cached_result

        logger.info("LLM_INTERPRET_CACHE_MISS")
        return _intent_cache.get(normalized) or {"intent": None, "entities": {}, "confidence": 0.0}

    @classmethod
    def generate_explore_response(cls, user_input: str) -> Optional[str]:
        """Generate a full conversational response for Explore Mode."""
        if not LLM_ENABLED:
            return None

        prompt = (
            "You are SmartElect, a civic assistant for India.\n\n"
            "Your role:\n"
            "* Explain voting, registration, elections, and civic processes clearly\n"
            "* Adapt tone dynamically based on user input (e.g., Gen Z, simple explanation, analogy requests)\n"
            "* If user explicitly asks for analogy (e.g., pizza, cricket), follow it\n"
            "* Be conversational and natural, not robotic\n\n"
            "STRICT RULES:\n"
            "* Do NOT fabricate laws, deadlines, or official data\n"
            '* If unsure -> say "This may vary by state or election cycle"\n'
            "* Do NOT claim user eligibility unless explicitly confirmed\n"
            "* No political bias, opinions, or persuasion\n\n"
            "STYLE:\n"
            "* Clear, structured but natural\n"
            "* Use examples, analogies when useful\n"
            "* Avoid robotic tone\n\n"
            f"User input: \"{user_input}\""
        )

        response_text = cls._generate_completion(prompt)
        if response_text:
            logger.info("LLM_EXPLORE_USED")
        return response_text
