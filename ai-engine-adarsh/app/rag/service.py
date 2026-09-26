"""RAG Service orchestrating retrieval, context assembly, LLM prompting, and source citations."""

import re
import time
from typing import List, Set
from app.core.logging import get_logger
from app.retrieval.models import RetrievalQuery, RetrievedChunk
from app.retrieval.service import retrieval_service
from app.providers.factory import get_llm_provider
from app.prompts.rag.grounded_qa import RAG_GROUNDED_SYSTEM_PROMPT, build_grounded_qa_prompt
from app.rag.models import RAGAnswer, RAGQueryRequest, SourceCitation
from app.rag.context_builder import ContextBuilder

logger = get_logger("app.rag.service")


class RAGService:
    """End-to-end Retrieval-Augmented Generation pipeline for grounded educational Q&A."""

    def __init__(self):
        self.llm = get_llm_provider()
        self.retrieval = retrieval_service

    def answer_query(self, request: RAGQueryRequest) -> RAGAnswer:
        """Executes full RAG workflow: retrieval -> context assembly -> generation -> citation mapping."""
        start_time = time.perf_counter()
        logger.info(f"Processing RAG query: '{request.query}'")

        # 1. Retrieve Candidate Chunks
        retrieval_req = RetrievalQuery(
            query=request.query,
            document_id=request.document_id,
            top_k=request.max_context_chunks,
            similarity_threshold=request.similarity_threshold,
        )
        retrieval_res = self.retrieval.query(retrieval_req)
        chunks: List[RetrievedChunk] = retrieval_res.results

        # Handle zero-relevance scenario
        if not chunks:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.warning(f"No relevant context found for query '{request.query}'")
            return RAGAnswer(
                query=request.query,
                answer=(
                    "I could not find sufficiently relevant information in the uploaded study material "
                    "to answer your question accurately. Please verify that the appropriate document is indexed."
                ),
                citations=[],
                source_chunk_ids=[],
                confidence_score=0.0,
                grounded=False,
                model_used=self.llm.model_name,
                latency_ms=elapsed_ms,
            )

        # 2. Assemble Context with Token Budget
        formatted_context, included_chunks, _ = ContextBuilder.assemble(
            chunks, max_token_budget=request.max_token_budget
        )

        chunk_map = {c.chunk_id: c for c in included_chunks}

        # 3. Build Prompt & Generate
        prompt = build_grounded_qa_prompt(request.query, formatted_context)
        generated_answer = self.llm.generate_text(
            prompt=prompt,
            system_instruction=RAG_GROUNDED_SYSTEM_PROMPT,
            temperature=request.temperature,
        )

        # 4. Extract Source Citations
        # Finds [Source: chk-xxx] or [Source:chk-xxx]
        cited_ids: Set[str] = set(re.findall(r"\[Source:\s*(chk-[a-zA-Z0-9\-]+)\]", generated_answer))

        citations: List[SourceCitation] = []
        for cid in cited_ids:
            if cid in chunk_map:
                chunk = chunk_map[cid]
                snippet = chunk.text[:120].strip() + ("..." if len(chunk.text) > 120 else "")
                citations.append(
                    SourceCitation(
                        chunk_id=chunk.chunk_id,
                        heading=chunk.heading,
                        page_number=chunk.page_number,
                        similarity_score=chunk.similarity_score,
                        snippet=snippet,
                    )
                )

        # If LLM didn't format explicit citations, cite the top included chunk
        if not citations and included_chunks:
            top_c = included_chunks[0]
            snippet = top_c.text[:120].strip() + ("..." if len(top_c.text) > 120 else "")
            citations.append(
                SourceCitation(
                    chunk_id=top_c.chunk_id,
                    heading=top_c.heading,
                    page_number=top_c.page_number,
                    similarity_score=top_c.similarity_score,
                    snippet=snippet,
                )
            )

        # 5. Compute Confidence Score
        avg_score = sum(c.similarity_score for c in included_chunks) / len(included_chunks)
        confidence = round(avg_score, 4)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            f"RAG query answered successfully in {elapsed_ms}ms with {len(citations)} citations."
        )

        return RAGAnswer(
            query=request.query,
            answer=generated_answer,
            citations=citations,
            source_chunk_ids=[c.chunk_id for c in included_chunks],
            confidence_score=confidence,
            grounded=True,
            model_used=self.llm.model_name,
            latency_ms=elapsed_ms,
        )


# Global singleton instance
rag_service = RAGService()
