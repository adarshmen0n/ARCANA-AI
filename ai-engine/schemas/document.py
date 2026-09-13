"""Document ingestion, extraction, and chunking schemas."""

from typing import Any, Dict, List, Optional
from pydantic import Field
from .base import ArcanaBaseModel, generate_id, current_utc_time


class Section(ArcanaBaseModel):
    """Represents a coherent section or subsection extracted from a document."""

    section_id: str = Field(default_factory=lambda: generate_id("sec"))
    title: str = Field(description="Heading or title of the section")
    level: int = Field(default=1, ge=1, le=6, description="Heading level (1=H1, 2=H2, etc.)")
    content: str = Field(description="Textual content within the section")
    page_start: Optional[int] = Field(default=None, description="Starting page or slide number")
    page_end: Optional[int] = Field(default=None, description="Ending page or slide number")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractedDocument(ArcanaBaseModel):
    """Normalized internal representation of an ingested document."""

    document_id: str = Field(default_factory=lambda: generate_id("doc"))
    filename: str = Field(description="Original name of the uploaded file")
    source_type: str = Field(description="MIME or file extension: pdf, docx, pptx, txt")
    title: str = Field(default="Untitled Document")
    sections: List[Section] = Field(default_factory=list)
    raw_text: str = Field(default="", description="Complete extracted text")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: current_utc_time().isoformat())


class Chunk(ArcanaBaseModel):
    """A semantic chunk of educational content with full traceability."""

    chunk_id: str = Field(default_factory=lambda: generate_id("chk"))
    document_id: str = Field(description="Parent document identifier")
    chapter: str = Field(default="", description="Chapter title or main topic")
    section: str = Field(default="", description="Section or subtopic title")
    text: str = Field(description="The semantic chunk text")
    page_start: Optional[int] = Field(default=None)
    page_end: Optional[int] = Field(default=None)
    chunking_version: str = Field(default="1.0")
    metadata: Dict[str, Any] = Field(default_factory=dict)
