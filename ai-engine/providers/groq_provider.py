"""Groq Cloud LLM Provider adapter.

Directly interacts with the GroqCloud OpenAI-compatible API using httpx without heavy SDKs,
delivering ultra-low-latency completions, structured output extraction, and streaming tokens.
"""

import json
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from .base import BaseLLMProvider

logger = logging.getLogger("arcana.providers.groq")
T = TypeVar("T", bound=BaseModel)


class GroqProvider(BaseLLMProvider):
    """High-throughput GroqCloud Provider with structured outputs and resilient failover."""

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(
        self,
        api_key: str,
        model_name: str = "openai/gpt-oss-20b",
        timeout_seconds: int = 30,
    ):
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
            headers = {"Authorization": f"Bearer {self.api_key}"}
            with httpx.Client(timeout=5) as client:
                res = client.get("https://api.groq.com/openai/v1/models", headers=headers)
                return res.status_code == 200
        except Exception:
            return False

    def _build_payload(self, prompt: str, system_prompt: Optional[str] = None, json_mode: bool = False, **kwargs: Any) -> Dict[str, Any]:
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": self._model_name,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.2),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        return payload

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = self._build_payload(prompt, system_prompt=system_prompt, **kwargs)

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self.BASE_URL, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Groq API error ({response.status_code}): {response.text}")
            data = response.json()
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                raise RuntimeError(f"Unexpected Groq response structure: {data}") from e

    async def generate_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = self._build_payload(prompt, system_prompt=system_prompt, **kwargs)

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(self.BASE_URL, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Groq API error ({response.status_code}): {response.text}")
            data = response.json()
            try:
                return data["choices"][0]["message"]["content"]
            except (KeyError, IndexError) as e:
                raise RuntimeError(f"Unexpected Groq response structure: {data}") from e

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
            "Do not output any explanation, markdown backticks, or intro text."
        )
        full_system = f"{system_prompt}\n\n{instruction}" if system_prompt else instruction

        raw_text = self.generate(prompt=prompt, system_prompt=full_system, json_mode=True, **kwargs)
        clean_text = raw_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.strip("`")
            if clean_text.startswith("json"):
                clean_text = clean_text[4:].strip()

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
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = self._build_payload(prompt, system_prompt=system_prompt, **kwargs)
        payload["stream"] = True

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            async with client.stream("POST", self.BASE_URL, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    raise RuntimeError(f"Groq API stream error ({response.status_code}): {await response.aread()}")
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        token_str = line[6:].strip()
                        if token_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(token_str)
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            continue
