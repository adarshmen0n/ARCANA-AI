"""Document Ingestion Engine orchestrating validation and format extraction."""

import logging
import time
from typing import Dict, Type
from schemas.document import ExtractedDocument
from .validator import DocumentValidator, DocumentValidationError
from .extractors import (
    BaseExtractor,
    TextExtractor,
    PDFExtractor,
    DocxExtractor,
    PPTXExtractor,
)

logger = logging.getLogger("arcana.ingestion.engine")


class DocumentIngestionEngine:
    """Coordinates file validation and deterministic text extraction across formats."""

    def __init__(self):
        self._extractors: Dict[str, BaseExtractor] = {
            "txt": TextExtractor(),
            "md": TextExtractor(),
            "pdf": PDFExtractor(),
            "docx": DocxExtractor(),
            "pptx": PPTXExtractor(),
        }

    def ingest(self, file_bytes: bytes, filename: str) -> ExtractedDocument:
        """Validate and extract structured content from document bytes.

        Args:
            file_bytes: Raw binary content of the file.
            filename: Original filename with extension.

        Returns:
            Normalized ExtractedDocument instance.

        Raises:
            DocumentValidationError: If validation fails.
            RuntimeError: If extraction fails.
        """
        start_time = time.perf_counter()

        # Step 1: Validate file sanity and format
        format_ext = DocumentValidator.validate(file_bytes, filename)

        extractor = self._extractors.get(format_ext)
        if not extractor:
            raise DocumentValidationError(f"No extractor registered for format '{format_ext}'.")

        # Step 2: Deterministic extraction
        try:
            doc = extractor.extract(file_bytes, filename)
        except Exception as e:
            logger.error("Extraction error for '%s' (%s): %s", filename, format_ext, e)
            raise RuntimeError(f"Failed to extract text from '{filename}': {str(e)}") from e

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Ingested '%s' (%s) in %.2fms: %d sections, %d chars",
            filename,
            format_ext,
            duration_ms,
            len(doc.sections),
            len(doc.raw_text),
        )

        doc.metadata["extraction_duration_ms"] = round(duration_ms, 2)
        return doc
