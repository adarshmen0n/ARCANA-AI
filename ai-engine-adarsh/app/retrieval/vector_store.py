"""In-memory Vector Store with NumPy-accelerated Cosine Similarity search."""

from typing import Dict, List, Optional, Tuple
import numpy as np
from app.embeddings.models import EmbeddedChunk


class InMemoryVectorStore:
    """Fast, local in-memory vector database supporting document-partitioned cosine similarity."""

    def __init__(self):
        self._chunks: Dict[str, EmbeddedChunk] = {}
        self._doc_index: Dict[str, List[str]] = {}

    def add_chunks(self, chunks: List[EmbeddedChunk]) -> int:
        """Stores embedded chunks into the vector index."""
        added_count = 0
        for chunk in chunks:
            self._chunks[chunk.chunk_id] = chunk
            if chunk.document_id not in self._doc_index:
                self._doc_index[chunk.document_id] = []
            if chunk.chunk_id not in self._doc_index[chunk.document_id]:
                self._doc_index[chunk.document_id].append(chunk.chunk_id)
            added_count += 1
        return added_count

    def search(
        self,
        query_vector: List[float],
        document_id: Optional[str] = None,
        top_k: int = 5,
        threshold: float = 0.25,
    ) -> Tuple[List[Tuple[EmbeddedChunk, float]], int]:
        """Performs cosine similarity search against indexed vector embeddings.

        Returns a tuple of (ranked_chunks_with_scores, total_candidates_searched).
        """
        # Determine candidate chunk pool
        if document_id:
            candidate_ids = self._doc_index.get(document_id, [])
        else:
            candidate_ids = list(self._chunks.keys())

        if not candidate_ids:
            return [], 0

        q_vec = np.array(query_vector, dtype=np.float32)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0.0:
            return [], len(candidate_ids)

        scored_candidates: List[Tuple[EmbeddedChunk, float]] = []
        seen_texts = set()

        for cid in candidate_ids:
            chunk = self._chunks[cid]
            c_vec = np.array(chunk.embedding, dtype=np.float32)
            c_norm = np.linalg.norm(c_vec)

            if c_norm == 0.0:
                continue

            similarity = float(np.dot(q_vec, c_vec) / (q_norm * c_norm))

            # Normalize to [0.0, 1.0] range
            normalized_score = max(0.0, min(1.0, (similarity + 1.0) / 2.0))

            if normalized_score >= threshold:
                # Deduplicate identical text
                if chunk.text not in seen_texts:
                    seen_texts.add(chunk.text)
                    scored_candidates.append((chunk, normalized_score))

        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        return scored_candidates[:top_k], len(candidate_ids)

    def count_chunks(self, document_id: Optional[str] = None) -> int:
        """Returns total indexed chunks, optionally scoped to a document."""
        if document_id:
            return len(self._doc_index.get(document_id, []))
        return len(self._chunks)

    def clear(self) -> None:
        """Resets the vector index."""
        self._chunks.clear()
        self._doc_index.clear()


# Global singleton instance
vector_store = InMemoryVectorStore()
