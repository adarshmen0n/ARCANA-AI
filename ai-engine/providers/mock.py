"""Mock LLM and Embedding providers for deterministic testing and offline development."""

import asyncio
import hashlib
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
import numpy as np
from pydantic import BaseModel
from .base import BaseLLMProvider, BaseEmbeddingProvider

T = TypeVar("T", bound=BaseModel)


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Deterministic, zero-network embedding provider for tests and benchmarking."""

    def __init__(self, dimension: int = 384, model_name: str = "mock-mini-embed"):
        self._dim = dimension
        self._name = model_name
        self._version = "1.0.0"

    def embed_text(self, text: str) -> List[float]:
        # Hash text to seed a deterministic random vector
        h = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(h[:4], "big")
        rng = np.random.RandomState(seed)
        vec = rng.randn(self._dim).astype(np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def model_name(self) -> str:
        return self._name

    @property
    def model_version(self) -> str:
        return self._version


class MockLLMProvider(BaseLLMProvider):
    """Deterministic, high-fidelity mock LLM for testing and development."""

    def __init__(self, model_name: str = "mock-arcana-model", should_fail: bool = False):
        self._name = model_name
        self.should_fail = should_fail
        self.call_count = 0

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError("Simulated provider failure in MockLLMProvider")
        return f"[MockLLM response to: '{prompt[:40]}...']"

    async def generate_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        await asyncio.sleep(0.01)
        return self.generate(prompt, system_prompt=system_prompt, **kwargs)

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        self.call_count += 1
        if self.should_fail:
            raise RuntimeError("Simulated structured failure in MockLLMProvider")

        # Dynamically build a sample valid model if possible, or construct default
        try:
            # Check fields of the model
            fields = response_model.model_fields
            data: Dict[str, Any] = {}
            for fname, field in fields.items():
                if field.default is not None and not str(field.default).startswith("PydanticUndefined"):
                    data[fname] = field.default
                elif field.default_factory is not None:
                    data[fname] = field.default_factory()
                else:
                    # Supply realistic defaults based on annotation
                    ann = str(field.annotation)
                    if "str" in ann:
                        data[fname] = f"Mock {fname.replace('_', ' ').title()}"
                    elif "int" in ann:
                        data[fname] = 2
                    elif "float" in ann:
                        data[fname] = 0.85
                    elif "bool" in ann:
                        data[fname] = True
                    elif "list" in ann.lower() or "List" in ann:
                        data[fname] = []
                    elif "dict" in ann.lower() or "Dict" in ann:
                        data[fname] = {}
                    else:
                        data[fname] = None
            return response_model.model_validate(data)
        except Exception:
            return response_model.model_construct()

    async def stream(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> AsyncIterator[str]:
        tokens = ["This ", "is ", "a ", "grounded ", "AI ", "Tutor ", "response."]
        for token in tokens:
            await asyncio.sleep(0.01)
            yield token

    def health_check(self) -> bool:
        return not self.should_fail

    @property
    def model_name(self) -> str:
        return self._name
