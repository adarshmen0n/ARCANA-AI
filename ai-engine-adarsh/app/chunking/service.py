"""Chunking Service for managing the end-to-end chunking pipeline."""

from typing import Dict, List, Optional
from app.core.errors import ResourceNotFoundException, ValidationException
from app.core.logging import get_logger
from app.ingestion.service import ingestion_service
from app.preprocessing.normalizer import normalize_text
from app.preprocessing.detector import detect_sections, SectionBlock
from app.chunking.models import ChunkingConfig, ChunkingResponse, DocumentChunk
from app.chunking.chunker import SemanticChunker

logger = get_logger("app.chunking.service")


class ChunkingService:
    """Coordinates preprocessing, section detection, semantic chunking, and retrieval indexing."""

    def __init__(self):
        self._chunks_by_document: Dict[str, List[DocumentChunk]] = {}
        self._chunks_by_id: Dict[str, DocumentChunk] = {}

    def chunk_document(
        self, document_id: str, config: Optional[ChunkingConfig] = None
    ) -> ChunkingResponse:
        """Runs normalization, section detection, and semantic chunking on an ingested document."""
        doc = ingestion_service.get_extracted_document(document_id)
        cfg = config or ChunkingConfig()
        chunker = SemanticChunker(cfg)

        logger.info(f"Chunking document {document_id} with strategy {cfg.strategy.value}")

        all_sections: List[SectionBlock] = []

        # If pages exist, process page by page to retain accurate page numbers
        if doc.pages:
            for page in doc.pages:
                cleaned_page_text = normalize_text(page.text)
                if cleaned_page_text:
                    page_sections = detect_sections(cleaned_page_text, default_page=page.page_number)
                    all_sections.extend(page_sections)
        else:
            cleaned_full_text = normalize_text(doc.full_text)
            all_sections = detect_sections(cleaned_full_text)

        chunks = chunker.chunk_sections(document_id, all_sections)

        if not chunks:
            raise ValidationException(f"Document {document_id} produced 0 chunks after normalization.")

        # Cache chunks
        self._chunks_by_document[document_id] = chunks
        for c in chunks:
            self._chunks_by_id[c.chunk_id] = c

        total_tokens = sum(c.token_count for c in chunks)
        logger.info(f"Generated {len(chunks)} chunks (~{total_tokens} tokens) for document {document_id}")

        return ChunkingResponse(
            document_id=document_id,
            total_chunks=len(chunks),
            total_tokens_estimated=total_tokens,
            chunks=chunks,
        )

    def get_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Retrieves cached chunks for a document. Chunks if not yet processed."""
        if document_id not in self._chunks_by_document:
            # Auto-chunk if document is extracted
            return self.chunk_document(document_id).chunks
        return self._chunks_by_document[document_id]

    def get_chunk_by_id(self, chunk_id: str) -> DocumentChunk:
        """Retrieves a single chunk by its chunk_id."""
        chunk = self._chunks_by_id.get(chunk_id)
        if not chunk:
            raise ResourceNotFoundException("DocumentChunk", chunk_id)
        return chunk


# Global singleton instance
chunking_service = ChunkingService()
