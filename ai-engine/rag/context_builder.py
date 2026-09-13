"""Context Builder for grounded educational RAG queries."""

from typing import List, Tuple
from schemas.document import Chunk
from retrieval.vector_store import RetrievalResult


class ContextBuilder:
    """Formats retrieved chunks into clean, bounded LLM context with citations."""

    @staticmethod
    def build_context(results: List[RetrievalResult], max_chars: int = 3000) -> Tuple[str, List[str]]:
        """Build formatted context string and list of referenced chunk IDs.

        Returns:
            Tuple of (formatted_context_string, list_of_chunk_ids).
        """
        if not results:
            return "No relevant educational source material found.", []

        context_blocks = []
        chunk_ids = []
        total_chars = 0

        for r in results:
            c: Chunk = r.chunk
            page_info = f", Page {c.page_start}" if c.page_start else ""
            block_header = f"[Source: {c.chapter} > {c.section}{page_info} | ID: {c.chunk_id}]"
            block = f"{block_header}\n{c.text}\n"

            if total_chars + len(block) > max_chars and context_blocks:
                break

            context_blocks.append(block)
            chunk_ids.append(c.chunk_id)
            total_chars += len(block)

        formatted_context = "\n---\n".join(context_blocks)
        return formatted_context, chunk_ids
