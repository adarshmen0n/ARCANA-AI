"""Data models for Document Chunking."""

from enum import Enum
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class ChunkingStrategy(str, Enum):
    SEMANTIC_SECTION = "semantic_section"
    SLIDING_WINDOW = "sliding_window"
    PARAGRAPH = "paragraph"


class ChunkingConfig(BaseModel):
    chunk_size_chars: int = Field(default=1200, ge=200, le=8000, description="Target chunk size in characters")
    chunk_overlap_chars: int = Field(default=200, ge=0, le=1000, description="Overlap between consecutive chunks")
    min_chunk_size_chars: int = Field(default=100, ge=20, description="Minimum characters for a valid chunk")
    strategy: ChunkingStrategy = Field(default=ChunkingStrategy.SEMANTIC_SECTION, description="Chunking strategy")


class DocumentChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier, e.g. chk-uuid-0001")
    document_id: str = Field(..., description="Parent document identifier")
    text: str = Field(..., min_length=1, description="Sanitized chunk text content")
    page_number: Optional[int] = Field(None, ge=1, description="Page number where chunk starts")
    chapter: Optional[str] = Field(None, description="Associated chapter heading if identified")
    section: Optional[str] = Field(None, description="Associated section heading or number")
    heading: str = Field(default="General", description="Nearest heading context")
    chunk_index: int = Field(..., ge=0, description="Zero-based sequential chunk index")
    token_count: int = Field(..., ge=0, description="Estimated token count (approx. len/4)")
    character_count: int = Field(..., ge=0, description="Total character count")
    content_type: str = Field(default="text", description="Category: text, code, table, heading")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )


class ChunkingResponse(BaseModel):
    document_id: str
    total_chunks: int
    total_tokens_estimated: int
    chunks: List[DocumentChunk]
