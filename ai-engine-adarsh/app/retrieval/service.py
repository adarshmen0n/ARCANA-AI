"""Retrieval Service coordinating chunk embedding, vector storage, and query retrieval."""

from typing import List
from app.core.logging import get_logger
from app.chunking.service import chunking_service
from app.embeddings.factory import get_embedding_provider
from app.embeddings.models import EmbeddedChunk
from app.retrieval.models import RetrievalQuery, RetrievalResponse, RetrievedChunk
from app.retrieval.vector_store import vector_store

logger = get_logger("app.retrieval.service")


class RetrievalService:
    """Manages vector indexing and top-k semantic retrieval for RAG pipelines."""

    def __init__(self):
        self.provider = get_embedding_provider()
        self.store = vector_store

    def index_document(self, document_id: str) -> int:
        """Embeds and indexes all semantic chunks for the specified document into the vector store."""
        chunks = chunking_service.get_chunks(document_id)
        logger.info(f"Indexing {len(chunks)} chunks for document {document_id}")

        embedded_chunks: List[EmbeddedChunk] = []

        # Batch embed chunk texts
        texts = [c.text for c in chunks]
        embeddings = self.provider.embed_batch(texts)

        for chunk, emb in zip(chunks, embeddings):
            embedded_chunks.append(
                EmbeddedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    text=chunk.text,
                    embedding=emb,
                    heading=chunk.heading,
                    page_number=chunk.page_number,
                    chapter=chunk.chapter,
                    section=chunk.section,
                )
            )

        added = self.store.add_chunks(embedded_chunks)
        logger.info(f"Successfully indexed {added} chunks for document {document_id}")
        return added

    def query(self, query_request: RetrievalQuery) -> RetrievalResponse:
        """Executes a semantic vector query, ranking results by cosine similarity."""
        logger.info(
            f"Executing retrieval query '{query_request.query}' "
            f"[doc_filter={query_request.document_id}, top_k={query_request.top_k}, thresh={query_request.similarity_threshold}]"
        )

        # Automatically index document if not yet indexed and document_id is provided
        if query_request.document_id and self.store.count_chunks(query_request.document_id) == 0:
            logger.info(f"Document {query_request.document_id} not yet indexed in vector store; indexing on-demand.")
            self.index_document(query_request.document_id)

        # Embed query text
        query_vector = self.provider.embed_text(query_request.query)

        # Search vector store
        ranked_chunks, total_searched = self.store.search(
            query_vector=query_vector,
            document_id=query_request.document_id,
            top_k=query_request.top_k,
            threshold=query_request.similarity_threshold,
        )

        results = [
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                text=chunk.text,
                heading=chunk.heading,
                page_number=chunk.page_number,
                similarity_score=round(score, 4),
            )
            for chunk, score in ranked_chunks
        ]

        logger.info(f"Retrieval yielded {len(results)} chunks from {total_searched} candidate vectors.")

        return RetrievalResponse(
            query=query_request.query,
            document_id_filter=query_request.document_id,
            total_candidates_searched=total_searched,
            retrieved_count=len(results),
            results=results,
        )


# Global singleton instance
retrieval_service = RetrievalService()
