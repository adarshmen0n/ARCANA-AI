"""Google Gemini LLM Provider implementation using official google-genai SDK."""

import json
import re
import time
from typing import Optional, Type, TypeVar
from pydantic import BaseModel

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from app.core.config import settings
from app.core.logging import get_logger
from app.providers.base import BaseLLMProvider
from app.providers.mock_provider import MockLLMProvider

T = TypeVar("T", bound=BaseModel)
logger = get_logger("app.providers.gemini")


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini model provider with native structured JSON enforcement and robust fallback."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self._model_name = model_name or settings.DEFAULT_MODEL
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._fallback = MockLLMProvider(model_name="mock-fallback")

        self._client = None
        if GENAI_AVAILABLE and self.api_key and not self.api_key.startswith("your_"):
            try:
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized live Google GenAI Client with model: {self._model_name}")
            except Exception as e:
                logger.warning(f"Could not initialize live GenAI Client ({e}). Fallback active.")

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
        """Generates natural language response from live Gemini model with automatic fallback."""
        if not self._client:
            logger.debug("Live Gemini client not active. Using deterministic fallback provider.")
            return self._fallback.generate_text(prompt, system_instruction, max_tokens, temperature)

        retries = 3
        for attempt in range(1, retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                    ),
                )
                if response and response.text:
                    return response.text
                logger.warning("Empty response from live Gemini API.")
                break
            except Exception as e:
                logger.warning(f"Live Gemini API text generation failed (attempt {attempt}/{retries}): {e}")
                if attempt < retries:
                    time.sleep(1.0 * (2 ** (attempt - 1)))

        logger.warning("Gemini API call unsuccessful. Falling back to local deterministic provider.")
        return self._fallback.generate_text(prompt, system_instruction, max_tokens, temperature)

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """Generates structured JSON adhering to the provided Pydantic schema using Gemini native schema validation."""
        if not self._client:
            logger.debug("Live Gemini client not active. Using deterministic fallback schema provider.")
            return self._fallback.generate_structured(prompt, schema, system_instruction, temperature)

        retries = 3
        for attempt in range(1, retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=temperature,
                        response_mime_type="application/json",
                        response_schema=schema,
                    ),
                )
                if response.parsed is not None and isinstance(response.parsed, schema):
                    return response.parsed
                if response.text:
                    # Clean markdown code fences if model returned raw JSON string
                    cleaned = re.sub(r"^```(?:json)?\s*", "", response.text.strip(), flags=re.IGNORECASE)
                    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
                    data = json.loads(cleaned)
                    return schema.model_validate(data)
            except Exception as e:
                logger.warning(f"Live Gemini structured generation attempt {attempt}/{retries} failed: {e}")
                if attempt < retries:
                    time.sleep(1.0 * (2 ** (attempt - 1)))

        logger.warning("Live Gemini structured generation exhausted. Falling back to deterministic generator.")
        return self._fallback.generate_structured(prompt, schema, system_instruction, temperature)
