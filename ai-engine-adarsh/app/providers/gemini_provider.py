"""Google Gemini LLM Provider implementation with retries, structured JSON, and fallback."""

import json
import re
import time
from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import MockLLMProvider

T = TypeVar("T", bound=BaseModel)
logger = get_logger("app.providers.gemini")

GEMINI_GENERATE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini model provider with structured JSON enforcement and fallback."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self._model_name = model_name or settings.DEFAULT_MODEL
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._fallback = MockLLMProvider(model_name="mock-fallback")

    @property
    def model_name(self) -> str:
        return self._model_name

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> str:
        """Generates natural language response from Gemini model."""
        if not self.api_key or self.api_key.startswith("your_"):
            logger.warning("No valid Gemini API key configured. Using deterministic fallback LLM provider.")
            return self._fallback.generate_text(prompt, system_instruction, max_tokens, temperature)

        url = f"{GEMINI_GENERATE_URL}/{self._model_name}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        retries = 3
        for attempt in range(1, retries + 1):
            try:
                with httpx.Client(timeout=20.0) as client:
                    response = client.post(url, json=payload, headers={"Content-Type": "application/json"})

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                    logger.error("Gemini response missing expected content structure.")
                    break

                if response.status_code in (429, 503):
                    time.sleep(1.0 * (2 ** (attempt - 1)))
                    continue

                logger.error(f"Gemini API returned error {response.status_code}: {response.text}")
                break

            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt}/{retries}): {str(e)}")
                if attempt < retries:
                    time.sleep(1.0 * (2 ** (attempt - 1)))

        logger.warning("Gemini API exhausted retries. Falling back to mock generator.")
        return self._fallback.generate_text(prompt, system_instruction, max_tokens, temperature)

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """Generates structured JSON adhering to the provided Pydantic schema."""
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        augmented_system = (
            (system_instruction or "") + "\n\n"
            "CRITICAL: Output ONLY valid raw JSON adhering to this JSON Schema. "
            "No markdown formatting, no conversational text, no explanations outside the JSON:\n"
            f"{schema_json}"
        )

        raw_response = self.generate_text(
            prompt=prompt,
            system_instruction=augmented_system,
            temperature=temperature,
        )

        # Parse JSON
        try:
            # Strip code fences if present
            cleaned = re.sub(r"^```(?:json)?\s*", "", raw_response.strip(), flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned.strip())
            data = json.loads(cleaned)
            return schema.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to parse structured JSON from model response ({str(e)}). Using fallback schema generator.")
            return self._fallback.generate_structured(prompt, schema, system_instruction, temperature)
