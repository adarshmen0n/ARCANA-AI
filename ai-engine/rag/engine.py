"""RAG Engine providing grounded answers with source citations."""

import logging
from typing import List, Optional
from schemas.base import ArcanaBaseModel
from embeddings.engine import EmbeddingEngine
from retrieval.vector_store import VectorStore
from providers.router import ProviderRouter
from .context_builder import ContextBuilder

logger = logging.getLogger("arcana.rag.engine")


class GroundedAnswer(ArcanaBaseModel):
    """Response from the RAG engine with verifiable source references."""

    query: str
    answer: str
    source_chunk_ids: List[str]
    retrieval_count: int


class RAGEngine:
    """Subsystem for retrieving relevant source material and generating grounded answers."""

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_engine: EmbeddingEngine,
        provider_router: ProviderRouter,
    ):
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        self.provider_router = provider_router

    def query(
        self,
        query_text: str,
        top_k: int = 4,
        document_id: Optional[str] = None,
        chapter: Optional[str] = None,
    ) -> GroundedAnswer:
        """Retrieve relevant source chunks and generate a grounded, factual answer."""
        # Step 1: Embed query
        query_vector = self.embedding_engine.embed_text(query_text)

        # Step 2: Retrieve candidate chunks
        results = self.vector_store.search(
            query_vector=query_vector,
            top_k=top_k,
            threshold=None,
            document_id=document_id,
            chapter=chapter,
        )

        # Step 3: Build bounded context with citations
        context_str, chunk_ids = ContextBuilder.build_context(results)

        # Step 4: Prompt LLM with strict grounding instructions
        system_prompt = (
            "You are the ARCANA Educational RAG Engine. Answer the user question using ONLY "
            "the provided source context. If the source material does not contain the information "
            "necessary to answer, state clearly: 'The uploaded educational material does not contain "
            "information regarding this topic.' Do NOT extrapolate or hallucinate outside the context."
        )

        user_prompt = f"Context:\n{context_str}\n\nQuestion: {query_text}\nAnswer:"

        answer_text = self.provider_router.generate(user_prompt, system_prompt=system_prompt)

        return GroundedAnswer(
            query=query_text,
            answer=answer_text.strip(),
            source_chunk_ids=chunk_ids,
            retrieval_count=len(results),
        )
