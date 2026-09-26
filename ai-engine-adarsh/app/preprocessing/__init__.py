"""Preprocessing Subsystem for text normalization, cleaning, and structure detection."""

from .normalizer import normalize_text, clean_whitespace, repair_hyphenation
from .detector import detect_sections, SectionBlock

__all__ = [
    "normalize_text",
    "clean_whitespace",
    "repair_hyphenation",
    "detect_sections",
    "SectionBlock",
]
