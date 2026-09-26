"""Base abstract extractor class for all file types."""

from abc import ABC, abstractmethod
from app.ingestion.models import DocumentMetadata, ExtractedDocument


class BaseExtractor(ABC):
    """Abstract interface for extracting text content and structural boundaries from documents."""

    @abstractmethod
    def extract(self, content: bytes, metadata: DocumentMetadata) -> ExtractedDocument:
        """Extracts structured text and pages from raw binary content."""
        pass
