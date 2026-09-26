"""Extractors package for parsing educational documents."""

from .base import BaseExtractor
from .factory import get_extractor

__all__ = ["BaseExtractor", "get_extractor"]
