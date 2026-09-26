"""PDF Extractor using PyPDF."""

import io
from typing import List
from pypdf import PdfReader
from app.ingestion.extractors.base import BaseExtractor
from app.ingestion.models import DocumentMetadata, ExtractedDocument, ExtractedPage, DocumentStatus


class PDFExtractor(BaseExtractor):
    """Extracts text page-by-page from PDF files."""

    def extract(self, content: bytes, metadata: DocumentMetadata) -> ExtractedDocument:
        stream = io.BytesIO(content)
        reader = PdfReader(stream)

        pages: List[ExtractedPage] = []
        all_text_parts: List[str] = []

        for idx, page in enumerate(reader.pages, start=1):
            try:
                page_text = page.extract_text() or ""
            except Exception:
                page_text = ""

            clean_page_text = page_text.strip()
            pages.append(
                ExtractedPage(
                    page_number=idx,
                    text=clean_page_text,
                    character_count=len(clean_page_text),
                )
            )
            if clean_page_text:
                all_text_parts.append(clean_page_text)

        full_text = "\n\n".join(all_text_parts)
        metadata.total_pages = len(pages)
        metadata.total_characters = len(full_text)
        metadata.status = DocumentStatus.EXTRACTED

        return ExtractedDocument(metadata=metadata, full_text=full_text, pages=pages)
