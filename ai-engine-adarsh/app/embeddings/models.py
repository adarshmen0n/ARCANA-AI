"""Data models for Embeddings Subsystem."""

from typing import List, Optional
from pydantic import BaseModel, Field


class EmbeddedChunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Associated document ID")
    text: str = Field(..., description="Chunk text content")
    embedding: List[float] = Field(..., description="Dense float vector embedding")
    heading: str = Field(default="General", description="Structural section heading")
    page_number: Optional[int] = Field(None, description="Source page number")
    chapter: Optional[str] = Field(None, description="Chapter context")
    section: Optional[str] = Field(None, description="Section context")
