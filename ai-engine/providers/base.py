"""Abstract provider contracts for LLM and Embedding models."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract interface for Language Model providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        """Generate free-form text completion."""
        pass

    @abstractmethod
    async def generate_async(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        """Asynchronously generate free-form text completion."""
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """Generate structured output validated against a Pydantic model."""
        pass

    @abstractmethod
    async def stream(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream conversational tokens."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify model accessibility and responsiveness."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return identifier of the model."""
        pass


class BaseEmbeddingProvider(ABC):
    """Abstract interface for Embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate vector embedding for a single text."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a batch of texts."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Vector dimensionality."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Embedding model identifier."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Model version identifier."""
        pass
