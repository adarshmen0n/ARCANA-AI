"""Deterministic Mock LLM Provider for offline testing and rapid local execution."""

import json
import re
from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from app.providers.base import BaseLLMProvider

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(BaseLLMProvider):
    """Generates predictable, grounded responses for tests without requiring API keys."""

    def __init__(self, model_name: str = "mock-llm-engine"):
        self._model_name = model_name

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
        """Synthesizes a grounded response referencing source chunks in the prompt."""
        # Find any [Source: chunk_id] or [Chunk: ...] patterns in the prompt
        chunk_matches = re.findall(r"\[Chunk:\s*(chk-[a-zA-Z0-9\-]+)\]", prompt)

        if not chunk_matches:
            # Fallback search for chunk ids
            chunk_matches = re.findall(r"(chk-[a-zA-Z0-9\-]+)", prompt)

        citations_str = ""
        if chunk_matches:
            unique_chunks = list(dict.fromkeys(chunk_matches))
            citations_str = " " + " ".join(f"[Source: {cid}]" for cid in unique_chunks[:2])

        # Extract query if present
        query_match = re.search(r"Question:\s*(.+?)(?:\n|$)", prompt, re.IGNORECASE)
        query_topic = query_match.group(1).strip() if query_match else "the requested concept"

        return (
            f"Based on the curriculum study material, {query_topic} is an essential educational concept. "
            f"Processes are scheduled according to defined algorithmic policies.{citations_str}"
        )

    def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_instruction: Optional[str] = None,
        temperature: float = 0.1,
    ) -> T:
        """Synthesizes structured Pydantic objects matching schema field requirements."""
        # Check if prompt contains raw JSON to parse
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", prompt, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return schema.model_validate(data)
            except Exception:
                pass

        # Build dummy instance from field definitions
        from pydantic_core import PydanticUndefined

        dummy_data = {}
        for field_name, field_info in schema.model_fields.items():
            annotation = field_info.annotation
            default = field_info.default

            if default is not PydanticUndefined and default is not None:
                dummy_data[field_name] = default
            elif annotation is str or (isinstance(annotation, type) and issubclass(annotation, str)) or str in getattr(annotation, "__args__", ()):
                dummy_data[field_name] = f"Mock {field_name.replace('_', ' ').title()}"
            elif annotation is int or (isinstance(annotation, type) and issubclass(annotation, int)):
                dummy_data[field_name] = 1
            elif annotation is float or (isinstance(annotation, type) and issubclass(annotation, float)):
                dummy_data[field_name] = 0.5
            elif annotation is bool:
                dummy_data[field_name] = True
            elif getattr(annotation, "__origin__", None) is list:
                dummy_data[field_name] = []
            elif getattr(annotation, "__origin__", None) is dict:
                dummy_data[field_name] = {}
            else:
                try:
                    dummy_data[field_name] = annotation()
                except Exception:
                    dummy_data[field_name] = f"Mock {field_name}"

        return schema.model_validate(dummy_data)
