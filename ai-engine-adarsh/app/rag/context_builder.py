"""Context Builder for assembling grounded, token-budgeted prompt contexts."""

from typing import List, Tuple
from app.retrieval.models import RetrievedChunk


class ContextBuilder:
    """Assembles retrieved chunks into formatted prompt context while enforcing token budgets."""

    @staticmethod
    def assemble(
        chunks: List[RetrievedChunk],
        max_token_budget: int = 2000,
    ) -> Tuple[str, List[RetrievedChunk], int]:
        """Formats chunks into an annotated context string respecting token limits.

        Returns (formatted_context_string, list_of_included_chunks, total_estimated_tokens).
        """
        included: List[RetrievedChunk] = []
        formatted_blocks: List[str] = []
        current_tokens = 0

        for idx, chunk in enumerate(chunks, start=1):
            page_info = f", Page: {chunk.page_number}" if chunk.page_number else ""
            block_header = f"[Chunk: {chunk.chunk_id}] (Section: {chunk.heading}{page_info})"
            block_text = f"{block_header}\n{chunk.text.strip()}"

            # Estimate tokens (~4 characters per token)
            block_tokens = max(1, len(block_text) // 4)

            if current_tokens + block_tokens > max_token_budget and included:
                # Token budget reached, skip remaining lower-ranked chunks
                break

            formatted_blocks.append(f"--- Context Block {idx} ---\n{block_text}")
            included.append(chunk)
            current_tokens += block_tokens

        formatted_context = "\n\n".join(formatted_blocks)
        return formatted_context, included, current_tokens
