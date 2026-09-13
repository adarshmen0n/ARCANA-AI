"""File and input validation for document ingestion.

Ensures uploaded educational material conforms to security, format,
and size constraints before any processing occurs.
"""

from pathlib import Path
from typing import Set

SUPPORTED_EXTENSIONS: Set[str] = {".pdf", ".docx", ".pptx", ".txt"}
MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB limit


class DocumentValidationError(Exception):
    """Raised when an uploaded document fails security or format validation."""
    pass


class DocumentValidator:
    """Deterministic validator for ingested files."""

    @staticmethod
    def validate(file_bytes: bytes, filename: str) -> str:
        """Validate file size, extension, and content sanity.

        Returns:
            Normalized file extension without leading dot (e.g. 'pdf', 'docx').

        Raises:
            DocumentValidationError: If file violates any safety rule.
        """
        if not filename or not filename.strip():
            raise DocumentValidationError("Filename must not be empty.")

        path = Path(filename)
        ext = path.suffix.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            raise DocumentValidationError(
                f"Unsupported format '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        if not file_bytes or len(file_bytes) == 0:
            raise DocumentValidationError(f"File '{filename}' is empty (0 bytes).")

        if len(file_bytes) > MAX_FILE_SIZE_BYTES:
            max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
            size_mb = len(file_bytes) / (1024 * 1024)
            raise DocumentValidationError(
                f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {max_mb} MB."
            )

        # Magic bytes check for format integrity
        clean_ext = ext.lstrip(".")
        if clean_ext == "pdf" and not file_bytes.startswith(b"%PDF"):
            raise DocumentValidationError(f"File '{filename}' does not have a valid PDF header.")

        if clean_ext in {"docx", "pptx"} and not file_bytes.startswith(b"PK\x03\x04"):
            raise DocumentValidationError(
                f"File '{filename}' is not a valid Office Open XML ZIP package."
            )

        return clean_ext
