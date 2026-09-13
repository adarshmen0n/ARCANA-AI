"""Abstract Base Class for format-specific extractors."""

from abc import ABC, abstractmethod
from schemas.document import ExtractedDocument


class BaseExtractor(ABC):
    """Abstract contract for extracting structured text and sections from files."""

    @abstractmethod
    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        """Extract structured sections and metadata from file bytes."""
        pass
