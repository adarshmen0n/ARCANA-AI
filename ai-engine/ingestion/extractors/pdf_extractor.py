"""PDF Extractor using pypdf for deterministic text and layout extraction."""

import io
import logging
from typing import List
from pypdf import PdfReader
from schemas.document import ExtractedDocument, Section
from schemas.base import generate_id
from .base import BaseExtractor

logger = logging.getLogger("arcana.ingestion.pdf")


class PDFExtractor(BaseExtractor):
    """Deterministic extractor for PDF documents."""

    def extract(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        stream = io.BytesIO(file_bytes)
        reader = PdfReader(stream)
        num_pages = len(reader.pages)

        sections: List[Section] = []
        all_text_parts: List[str] = []

        # Extract page by page, tracking page numbers
        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            try:
                page_text = page.extract_text() or ""
            except Exception as e:
                logger.warning("Failed to extract page %d from %s: %s", page_num, filename, e)
                page_text = ""

            page_text_clean = page_text.strip()
            if page_text_clean:
                all_text_parts.append(page_text_clean)
                first_line = page_text_clean.splitlines()[0][:80]
                section_title = first_line if len(first_line) > 3 else f"Page {page_num}"
                sections.append(
                    Section(
                        section_id=generate_id("sec"),
                        title=section_title,
                        level=1,
                        content=page_text_clean,
                        page_start=page_num,
                        page_end=page_num,
                        metadata={"page_number": page_num},
                    )
                )

        full_text = "\n\n".join(all_text_parts)
        metadata = {
            "total_pages": num_pages,
            "char_count": len(full_text),
        }
        if reader.metadata:
            title = reader.metadata.title or filename.rsplit(".", 1)[0]
            if reader.metadata.author:
                metadata["author"] = str(reader.metadata.author)
        else:
            title = filename.rsplit(".", 1)[0]

        return ExtractedDocument(
            document_id=generate_id("doc"),
            filename=filename,
            source_type="pdf",
            title=str(title),
            sections=sections,
            raw_text=full_text,
            metadata=metadata,
        )
