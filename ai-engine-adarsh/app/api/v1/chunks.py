"""Chunking API Endpoints."""

from typing import List, Optional
from fastapi import APIRouter, status
from app.chunking.models import ChunkingConfig, ChunkingResponse, DocumentChunk
from app.chunking.service import chunking_service

router = APIRouter(tags=["Chunks"])


@router.post(
    "/documents/{document_id}/chunks",
    response_model=ChunkingResponse,
    status_code=status.HTTP_200_OK,
)
async def create_document_chunks(
    document_id: str,
    config: Optional[ChunkingConfig] = None,
) -> ChunkingResponse:
    """Normalizes and chunks an extracted document into structured semantic blocks."""
    return chunking_service.chunk_document(document_id, config)


@router.get(
    "/documents/{document_id}/chunks",
    response_model=List[DocumentChunk],
    status_code=status.HTTP_200_OK,
)
async def get_document_chunks(document_id: str) -> List[DocumentChunk]:
    """Retrieves all semantic chunks generated for an ingested document."""
    return chunking_service.get_chunks(document_id)


@router.get(
    "/chunks/{chunk_id}",
    response_model=DocumentChunk,
    status_code=status.HTTP_200_OK,
)
async def get_chunk_by_id(chunk_id: str) -> DocumentChunk:
    """Retrieves a single chunk by its unique chunk_id for source grounding."""
    return chunking_service.get_chunk_by_id(chunk_id)
