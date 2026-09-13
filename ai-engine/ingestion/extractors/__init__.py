"""Document extractors package."""

from .base import BaseExtractor
from .txt_extractor import TextExtractor
from .pdf_extractor import PDFExtractor
from .docx_extractor import DocxExtractor
from .pptx_extractor import PPTXExtractor

__all__ = ["BaseExtractor", "TextExtractor", "PDFExtractor", "DocxExtractor", "PPTXExtractor"]
