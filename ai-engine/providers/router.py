"""Provider router and resilient model orchestrator.

Manages primary and fallback LLM providers, bounded exponential backoff retries,
and structured output validation.
"""

import logging
import time
from typing import Any, AsyncIterator, List, Optional, Type, TypeVar
from pydantic import BaseModel
from .base import BaseLLMProvider, BaseEmbeddingProvider
from .mock import MockLLMProvider, MockEmbeddingProvider
from .gemini_provider import GeminiProvider
from config.settings import get_settings

logger = logging.getLogger("arcana.providers.router")
T = TypeVar("T", bound=BaseModel)


class ProviderRouter:
    """Routes generation requests between primary and fallback providers with bounded retries."""

    def __init__(
        self,
        primary_provider: Optional[BaseLLMProvider] = None,
        fallback_provider: Optional[BaseLLMProvider] = None,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
        max_retries: int = 3,
        initial_backoff_sec: float = 0.5,
    ):
        settings = get_settings()
        self.max_retries = max_retries or settings.LLM_MAX_RETRIES
        self.initial_backoff_sec = initial_backoff_sec

        # Initialize primary LLM
        if primary_provider:
            self.primary = primary_provider
        elif settings.PRIMARY_LLM_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            self.primary = GeminiProvider(api_key=settings.GEMINI_API_KEY)
        else:
            self.primary = MockLLMProvider(model_name="mock-primary")

        # Initialize fallback LLM
        if fallback_provider:
            self.fallback = fallback_provider
        else:
            self.fallback = MockLLMProvider(model_name="mock-fallback")

        # Initialize embedding provider
        if embedding_provider:
            self.embedding_provider = embedding_provider
        else:
            self.embedding_provider = MockEmbeddingProvider()

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any) -> str:
        """Generate text with primary provider, failing over to fallback on error."""
        providers: List[BaseLLMProvider] = [self.primary, self.fallback]

        last_error = None
        for provider in providers:
            backoff = self.initial_backoff_sec
            for attempt in range(1, self.max_retries + 1):
                try:
                    start_t = time.perf_counter()
                    result = provider.generate(prompt, system_prompt=system_prompt, **kwargs)
                    latency = (time.perf_counter() - start_t) * 1000
                    logger.debug(
                        "Generated text using %s in %.2fms (attempt %d)",
                        provider.model_name,
                        latency,
                        attempt,
                    )
                    return result
                except Exception as e:
                    last_error = e
                    logger.warning(
                        "Provider %s attempt %d failed: %s",
                        provider.model_name,
                        attempt,
                        e,
                    )
                    if attempt < self.max_retries:
                        time.sleep(backoff)
                        backoff *= 2.0
            logger.error("Provider %s exhausted retries. Switching to next provider.", provider.model_name)

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """Generate structured Pydantic object with primary or fallback provider."""
        providers: List[BaseLLMProvider] = [self.primary, self.fallback]

        last_error = None
        for provider in providers:
            backoff = self.initial_backoff_sec
            for attempt in range(1, self.max_retries + 1):
                try:
                    start_t = time.perf_counter()
                    result = provider.generate_structured(
                        prompt,
                        response_model=response_model,
                        system_prompt=system_prompt,
                        **kwargs,
                    )
                    latency = (time.perf_counter() - start_t) * 1000
                    logger.debug(
                        "Generated structured %s using %s in %.2fms",
                        response_model.__name__,
                        provider.model_name,
                        latency,
                    )
                    return result
                except Exception as e:
                    last_error = e
                    logger.warning(
                        "Structured generation with %s failed (attempt %d): %s",
                        provider.model_name,
                        attempt,
                        e,
                    )
                    if attempt < self.max_retries:
                        time.sleep(backoff)
                        backoff *= 2.0
            logger.error("Provider %s failed for structured output. Trying fallback.", provider.model_name)

        raise RuntimeError(f"All providers failed structured output for {response_model.__name__}: {last_error}")

    def embed_text(self, text: str) -> List[float]:
        return self.embedding_provider.embed_text(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedding_provider.embed_documents(texts)
