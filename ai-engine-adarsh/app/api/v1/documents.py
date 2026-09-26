"""Document Ingestion API Endpoints."""

from typing import List
from fastapi import APIRouter, BackgroundTasks, File, UploadFile, status
from app.ingestion.models import (
    DocumentMetadata,
    DocumentStatusResponse,
    DocumentUploadResponse,
    ExtractedDocument,
)
from app.ingestion.service import ingestion_service

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Educational document (PDF, DOCX, PPTX, TXT)"),
) -> DocumentUploadResponse:
    """Uploads an educational document and schedules asynchronous background extraction."""
    content = await file.read()
    metadata = ingestion_service.register_upload(file.filename or "unknown.txt", content)

    # Queue async extraction in background worker
    background_tasks.add_task(ingestion_service.process_document, metadata.document_id, content)

    return DocumentUploadResponse(
        document_id=metadata.document_id,
        filename=metadata.filename,
        status=metadata.status,
        message="Document uploaded successfully. Processing started in background.",
        status_url=f"/api/v1/documents/{metadata.document_id}/status",
    )


@router.get("/{document_id}/status", response_model=DocumentStatusResponse, status_code=status.HTTP_200_OK)
async def get_document_status(document_id: str) -> DocumentStatusResponse:
    """Returns the current processing status and extraction metrics of a document."""
    meta = ingestion_service.get_metadata(document_id)
    return DocumentStatusResponse(
        document_id=meta.document_id,
        status=meta.status,
        filename=meta.filename,
        file_format=meta.file_format,
        total_pages=meta.total_pages,
        total_characters=meta.total_characters,
        uploaded_at=meta.uploaded_at,
        error=meta.error_message,
    )


@router.get("/{document_id}", response_model=DocumentMetadata, status_code=status.HTTP_200_OK)
async def get_document_metadata(document_id: str) -> DocumentMetadata:
    """Returns detailed metadata for an ingested document."""
    return ingestion_service.get_metadata(document_id)


@router.get("/{document_id}/content", response_model=ExtractedDocument, status_code=status.HTTP_200_OK)
async def get_extracted_content(document_id: str) -> ExtractedDocument:
    """Returns the full extracted text and structured pages of an ingested document."""
    return ingestion_service.get_extracted_document(document_id)


@router.get("", response_model=List[DocumentMetadata], status_code=status.HTTP_200_OK)
async def list_documents() -> List[DocumentMetadata]:
    """Lists all registered educational documents."""
    return ingestion_service.list_documents()
