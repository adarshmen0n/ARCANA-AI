"""Data models and schemas for Document Ingestion and Extraction."""

from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    FAILED = "failed"


class SupportedFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"


class ExtractedPage(BaseModel):
    page_number: int = Field(..., ge=1, description="1-indexed page or slide number")
    text: str = Field(..., description="Raw extracted text from page")
    character_count: int = Field(..., ge=0, description="Character count for this page")


class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique UUID v4 for the document")
    filename: str = Field(..., description="Original uploaded filename")
    file_format: SupportedFormat = Field(..., description="File format extension")
    file_size_bytes: int = Field(..., ge=0, description="Size of file in bytes")
    uploaded_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC upload timestamp",
    )
    status: DocumentStatus = Field(default=DocumentStatus.PENDING, description="Current ingestion status")
    total_pages: int = Field(default=0, ge=0, description="Total pages or slides extracted")
    total_characters: int = Field(default=0, ge=0, description="Total characters extracted")
    error_message: Optional[str] = Field(None, description="Error reason if extraction failed")


class ExtractedDocument(BaseModel):
    metadata: DocumentMetadata
    full_text: str = Field(..., description="Combined extracted raw text across all pages")
    pages: List[ExtractedPage] = Field(default_factory=list, description="Per-page structured text slices")


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="Assigned document UUID v4")
    filename: str = Field(..., description="Filename received")
    status: DocumentStatus = Field(..., description="Initial ingestion state")
    message: str = Field(..., description="Informational message")
    status_url: str = Field(..., description="Polling endpoint for progress checking")


class DocumentStatusResponse(BaseModel):
    document_id: str = Field(..., description="Document identifier")
    status: DocumentStatus = Field(..., description="Current status")
    filename: str
    file_format: SupportedFormat
    total_pages: int
    total_characters: int
    uploaded_at: str
    error: Optional[str] = None
