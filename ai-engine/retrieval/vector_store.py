"""In-memory numpy-vectorized vector store for semantic retrieval."""

from typing import Any, Dict, List, Optional
import numpy as np
from schemas.document import Chunk
from schemas.base import ArcanaBaseModel


class RetrievalResult(ArcanaBaseModel):
    """Result of a semantic vector search query."""

    chunk: Chunk
    score: float


class VectorStore:
    """Numpy-vectorized in-memory vector store supporting cosine similarity and metadata filtering."""

    def __init__(self):
        self._chunks: List[Chunk] = []
        self._vectors: Optional[np.ndarray] = None

    def add_chunks(self, chunks: List[Chunk], vectors: List[List[float]]) -> None:
        """Add chunks and corresponding embedding vectors to the index."""
        if not chunks or not vectors:
            return

        self._chunks.extend(chunks)
        new_vecs = np.array(vectors, dtype=np.float32)

        if self._vectors is None:
            self._vectors = new_vecs
        else:
            self._vectors = np.vstack([self._vectors, new_vecs])

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        threshold: Optional[float] = None,
        document_id: Optional[str] = None,
        chapter: Optional[str] = None,
        section: Optional[str] = None,
    ) -> List[RetrievalResult]:
        """Perform cosine similarity search with optional metadata filters."""
        if self._vectors is None or len(self._chunks) == 0:
            return []

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm

        # Vectorized dot product for cosine similarity
        scores = np.dot(self._vectors, q_vec)

        # Apply metadata filters
        candidates = []
        for idx, (chunk, score) in enumerate(zip(self._chunks, scores)):
            if threshold is not None and score < threshold:
                continue
            if document_id and chunk.document_id != document_id:
                continue
            if chapter and chunk.chapter.lower() != chapter.lower():
                continue
            if section and chunk.section.lower() != section.lower():
                continue
            candidates.append((chunk, float(score)))

        # Sort descending by score and slice top_k
        candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates[:top_k]

        return [RetrievalResult(chunk=c, score=s) for c, s in top_candidates]

    def clear(self) -> None:
        """Clear all stored vectors and chunks."""
        self._chunks = []
        self._vectors = None

    @property
    def total_chunks(self) -> int:
        return len(self._chunks)
