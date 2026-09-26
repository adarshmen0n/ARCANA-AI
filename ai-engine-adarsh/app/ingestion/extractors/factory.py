"""Extractor factory for dynamic extractor resolution."""

from typing import Dict, Type
from app.core.errors import ValidationException
from app.ingestion.extractors.base import BaseExtractor
from app.ingestion.extractors.pdf_extractor import PDFExtractor
from app.ingestion.extractors.docx_extractor import DOCXExtractor
from app.ingestion.extractors.pptx_extractor import PPTXExtractor
from app.ingestion.extractors.txt_extractor import TXTExtractor
from app.ingestion.models import SupportedFormat

_EXTRACTOR_REGISTRY: Dict[SupportedFormat, Type[BaseExtractor]] = {
    SupportedFormat.PDF: PDFExtractor,
    SupportedFormat.DOCX: DOCXExtractor,
    SupportedFormat.PPTX: PPTXExtractor,
    SupportedFormat.TXT: TXTExtractor,
}


def get_extractor(file_format: SupportedFormat) -> BaseExtractor:
    """Returns an instantiated extractor for the requested file format.

    Raises ValidationException if unsupported.
    """
    extractor_cls = _EXTRACTOR_REGISTRY.get(file_format)
    if not extractor_cls:
        raise ValidationException(f"No extractor registered for format: {file_format}")
    return extractor_cls()
