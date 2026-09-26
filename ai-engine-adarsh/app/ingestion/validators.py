"""File validators for Document Ingestion."""

import os
from typing import Tuple
from app.core.errors import ValidationException
from app.ingestion.models import SupportedFormat

# Maximum allowed upload size (25 MB by default)
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024

SUPPORTED_EXTENSIONS = {
    ".pdf": SupportedFormat.PDF,
    ".docx": SupportedFormat.DOCX,
    ".pptx": SupportedFormat.PPTX,
    ".txt": SupportedFormat.TXT,
}


def validate_file_metadata(filename: str, file_size: int) -> Tuple[str, SupportedFormat]:
    """Validates filename extension and size constraints.

    Returns the sanitized extension and SupportedFormat enum.
    Raises ValidationException if invalid.
    """
    if not filename or not filename.strip():
        raise ValidationException("Filename must not be empty.")

    if file_size <= 0:
        raise ValidationException(f"Uploaded file '{filename}' is empty (0 bytes).")

    if file_size > MAX_FILE_SIZE_BYTES:
        max_mb = MAX_FILE_SIZE_BYTES // (1024 * 1024)
        actual_mb = round(file_size / (1024 * 1024), 2)
        raise ValidationException(
            f"File size exceeds maximum permitted limit of {max_mb} MB (received {actual_mb} MB)."
        )

    _, ext = os.path.splitext(filename.lower())
    if ext not in SUPPORTED_EXTENSIONS:
        allowed = ", ".join(SUPPORTED_EXTENSIONS.keys())
        raise ValidationException(
            f"Unsupported file format '{ext}'. Allowed formats: {allowed}."
        )

    return ext, SUPPORTED_EXTENSIONS[ext]
