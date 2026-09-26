"""Plain Text (TXT) Extractor."""

from app.ingestion.extractors.base import BaseExtractor
from app.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage, DocumentStatus


class TXTExtractor(BaseExtractor):
    """Extracts text from raw plain text files with automatic encoding fallbacks."""

    def extract(self, content: bytes, metadata: DocumentMetadata) -> ExtractedDocument:
        # Try UTF-8 first, fallback to Latin-1
        try:
            full_text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                full_text = content.decode("latin-1")
            except UnicodeDecodeError:
                full_text = content.decode("utf-8", errors="replace")

        full_text = full_text.strip()

        pages = [
            ExtractedPage(
                page_number=1,
                text=full_text,
                character_count=len(full_text),
            )
        ]

        metadata.total_pages = 1
        metadata.total_characters = len(full_text)
        metadata.status = DocumentStatus.EXTRACTED

        return ExtractedDocument(metadata=metadata, full_text=full_text, pages=pages)
