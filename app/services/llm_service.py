"""LLM Service for SmartElect intent assistance and response polishing."""

import logging
import os
from typing import Optional

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
                # Assuming api key is set via GOOGLE_API_KEY environment variable
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
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
                return response.choices[0].message.content.strip() if response.choices else None
            else:
                logger.warning(f"Unknown LLM provider: {LLM_PROVIDER}")
                return None
        except Exception as e:
            logger.error(f"LLM integration failed: {e}")
            return None

    @classmethod
    def assist_intent(cls, user_input: str, allowed_intents: list[str]) -> Optional[str]:
        """Attempt to map unclear user input to a known structured intent."""
        if not LLM_ENABLED:
            return None

        prompt = (
            f"You are a routing assistant for a deterministic civic platform.\n"
            f"Map the user input to exactly one of the following intents: {allowed_intents}.\n"
            f"If it does not clearly match any of them, reply with 'out_of_scope'.\n"
            f"Reply with ONLY the intent name, nothing else.\n\n"
            f"User input: \"{user_input}\""
        )
        
        response_text = cls._generate_completion(prompt)
        
        if response_text and response_text in allowed_intents:
            return response_text
            
        return "out_of_scope"

    @classmethod
    def polish_response(cls, decision_content: str, decision_next_step: str, user_input: str) -> dict[str, str]:
        """Polish the structured response for clarity and flow, ensuring a calm, neutral tone."""
        if not LLM_ENABLED:
            return {"content": decision_content, "next_step": decision_next_step}

        prompt = (
            f"You are a highly structured, calm, and neutral civic assistant.\n"
            f"Your task is to rewrite the provided content and next step to improve readability, flow, and natural language.\n"
            f"CRITICAL RULES:\n"
            f"- Preserve the exact semantic meaning and all steps.\n"
            f"- Do NOT add new information, advice, or external links.\n"
            f"- Do NOT introduce opinions or evaluate any political entities.\n"
            f"- Maintain a calm, neutral, and professional tone. Avoid overly enthusiastic or cheerful phrasing (no exclamation points or hyperbole).\n"
            f"- Format the output clearly. Keep steps numbered or bulleted if they were originally.\n\n"
            f"Original User Input: \"{user_input}\"\n\n"
            f"Original Content:\n{decision_content}\n\n"
            f"Original Next Step:\n{decision_next_step}\n\n"
            f"Output the rewritten Content, followed by a '|||' separator, followed by the rewritten Next Step."
        )

        response_text = cls._generate_completion(prompt)
        
        if not response_text or "|||" not in response_text:
            return {"content": decision_content, "next_step": decision_next_step}
            
        parts = response_text.split("|||", 1)
        return {
            "content": parts[0].strip(),
            "next_step": parts[1].strip()
        }
