"""Embedding Engine with batching, normalization, and content hashing cache."""

import hashlib
import logging
from typing import Dict, List, Optional
from providers.base import BaseEmbeddingProvider
from providers.mock import MockEmbeddingProvider

logger = logging.getLogger("arcana.embeddings.engine")


class EmbeddingEngine:
    """Handles embedding generation with in-memory hashing cache to eliminate redundant computation."""

    def __init__(self, provider: Optional[BaseEmbeddingProvider] = None):
        self.provider = provider or MockEmbeddingProvider()
        self._cache: Dict[str, List[float]] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def _compute_cache_key(self, text: str) -> str:
        h = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
        return f"{self.provider.model_name}:{self.provider.model_version}:{h}"

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string, utilizing cache if available."""
        key = self._compute_cache_key(text)
        if key in self._cache:
            self.cache_hits += 1
            return self._cache[key]

        self.cache_misses += 1
        vector = self.provider.embed_text(text)
        self._cache[key] = vector
        return vector

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts, only requesting missing items from the provider."""
        results: List[Optional[List[float]]] = [None] * len(texts)
        missing_indices: List[int] = []
        missing_texts: List[str] = []

        for i, t in enumerate(texts):
            key = self._compute_cache_key(t)
            if key in self._cache:
                self.cache_hits += 1
                results[i] = self._cache[key]
            else:
                self.cache_misses += 1
                missing_indices.append(i)
                missing_texts.append(t)

        if missing_texts:
            new_vectors = self.provider.embed_documents(missing_texts)
            for idx, vec, txt in zip(missing_indices, new_vectors, missing_texts):
                key = self._compute_cache_key(txt)
                self._cache[key] = vec
                results[idx] = vec

        return [r for r in results if r is not None]

    @property
    def dimension(self) -> int:
        return self.provider.dimension
