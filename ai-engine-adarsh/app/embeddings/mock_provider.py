"""Deterministic Mock Embedding Provider for fast, offline, and reliable testing."""

import hashlib
import math
from typing import List
from app.embeddings.base import BaseEmbeddingProvider


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """Generates deterministic, L2-normalized float vectors for local testing and CI/CD."""

    def __init__(self, dimension: int = 256):
        self._dim = dimension

    @property
    def dimension(self) -> int:
        return self._dim

    def _hash_to_vector(self, text: str) -> List[float]:
        """Maps text to a normalized pseudo-semantic vector using term hashing and n-grams."""
        vector = [0.0] * self._dim
        words = text.lower().split()

        if not words:
            return vector

        for word in words:
            # Hash whole word
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dim
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vector[idx] += sign * 1.5

            # Hash character 3-grams for subword similarity
            for i in range(len(word) - 2):
                ngram = word[i : i + 3]
                nh = int(hashlib.sha256(ngram.encode("utf-8")).hexdigest(), 16)
                nidx = nh % self._dim
                nsign = 1.0 if ((nh >> 8) & 1) else -1.0
                vector[nidx] += nsign * 0.5

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0.0:
            vector = [x / norm for x in vector]

        return vector

    def embed_text(self, text: str) -> List[float]:
        return self._hash_to_vector(text)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_to_vector(t) for t in texts]
