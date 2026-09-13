"""Google Gemini LLM Provider adapter.

Directly interacts with Google Gemini REST API using httpx without heavy SDKs,
supporting structured output parsing and streaming tokens.
"""

import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from .base import BaseLLMProvider

logger = logging.getLogger("arcana.providers.gemini")
T = TypeVar("T", bound=BaseModel)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider with structured outputs and fallback resilience."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str, model_name: str = "gemini-3-flash-preview", timeout_seconds: int = 30):
        self.api_key = api_key
        self._model_name = model_name
        self.timeout_seconds = timeout_seconds

    @property
    def model_name(self) -> str:
        return self._model_name

    def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            url = f"{self.BASE_URL}/{self._model_name}?key={self.api_key}"
            with httpx.Client(timeout=5) as client:
                res = client.get(url)
                return res.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        url = f"{self.BASE_URL}/{self._model_name}:generateContent?key={self.api_key}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_prompt:
            payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text}")
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise RuntimeError(f"Unexpected Gemini response structure: {data}") from e

    async def generate_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        url = f"{self.BASE_URL}/{self._model_name}:generateContent?key={self.api_key}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_prompt:
            payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Gemini API error ({response.status_code}): {response.text}")
            data = response.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise RuntimeError(f"Unexpected Gemini response structure: {data}") from e

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        schema_json = json.dumps(response_model.model_json_schema())
        instruction = (
            f"You MUST respond ONLY with valid JSON conforming to this JSON Schema:\n{schema_json}\n"
            "Do not wrap in markdown or backticks."
        )
        full_system = f"{system_prompt}\n{instruction}" if system_prompt else instruction

        raw_text = self.generate(prompt=prompt, system_prompt=full_system, **kwargs)
        # Strip potential markdown fences
        clean_text = raw_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`")
            if clean_text.startswith("json"):
                clean_text = clean_text[4:].strip()

        # Find first { or [ and last } or ]
        start_idx = -1
        for i, ch in enumerate(clean_text):
            if ch in ("{", "["):
                start_idx = i
                break
        end_idx = -1
        for i in range(len(clean_text) - 1, -1, -1):
            if clean_text[i] in ("}", "]"):
                end_idx = i + 1
                break
        if start_idx != -1 and end_idx != -1:
            clean_text = clean_text[start_idx:end_idx]

        data = json.loads(clean_text)
        return response_model.model_validate(data)

    async def stream(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> AsyncIterator[str]:
        # Simple token generator for async streaming
        full_text = await self.generate_async(prompt, system_prompt=system_prompt, **kwargs)
        words = full_text.split(" ")
        for w in words:
            yield w + " "
