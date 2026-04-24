"""LLM Service for SmartElect intent assistance and response polishing."""

import json
import logging
import os
from typing import Optional, Any

logger = logging.getLogger(__name__)

# System flag to enable/disable LLM globally
LLM_ENABLED = os.getenv("LLM_ENABLED", "True").lower() in ("true", "1", "yes")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()


class LLMService:
    """Abstract service for safe, thin-layer LLM integration."""

    @classmethod
    def _generate_completion(cls, prompt: str) -> Optional[str]:
        """Wrapper to call the configured LLM provider."""
        if not LLM_ENABLED:
            return None

        try:
            if LLM_PROVIDER == "gemini":
                import google.generativeai as genai
                
                if not os.getenv("GOOGLE_API_KEY"):
                    logger.error("GOOGLE_API_KEY missing")
                    return None
                    
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                logger.info("LLM CALL SUCCESS")
                return response.text.strip()
            elif LLM_PROVIDER == "openai":
                import openai
                # Assuming api key is set via OPENAI_API_KEY environment variable
                client = openai.OpenAI()
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
    def interpret_user_input(cls, user_input: str) -> dict[str, Any]:
        """Extract intent and entities from user input, returning strict JSON."""
        if not LLM_ENABLED:
            return {"intent": None, "entities": {}, "confidence": 0.0}

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
            f"User input: \"{user_input}\""
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
