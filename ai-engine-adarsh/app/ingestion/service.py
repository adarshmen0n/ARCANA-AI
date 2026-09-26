"""Document Ingestion Service.

Orchestrates document registration, async background extraction, and state tracking.
"""

import uuid
from typing import Dict, List, Optional
from app.core.errors import ResourceNotFoundException, ValidationException
from app.core.logging import get_logger
from app.ingestion.extractors.factory import get_extractor
from app.ingestion.models import (
    DocumentMetadata,
    DocumentStatus,
    ExtractedDocument,
    SupportedFormat,
)
from app.ingestion.validators import validate_file_metadata

logger = get_logger("app.ingestion.service")


class IngestionService:
    """Manages document lifecycles from upload to structured extraction."""

    def __init__(self):
        # In-memory document stores (can be backed by persistence in Abhishek's backend)
        self._metadata_store: Dict[str, DocumentMetadata] = {}
        self._document_store: Dict[str, ExtractedDocument] = {}

    def register_upload(self, filename: str, content: bytes) -> DocumentMetadata:
        """Validates incoming file and creates initial metadata record in PENDING state."""
        file_size = len(content)
        _, file_format = validate_file_metadata(filename, file_size)

        document_id = str(uuid.uuid4())
        metadata = DocumentMetadata(
            document_id=document_id,
            filename=filename,
            file_format=file_format,
            file_size_bytes=file_size,
            status=DocumentStatus.PENDING,
        )

        self._metadata_store[document_id] = metadata
        logger.info(f"Registered document upload '{filename}' ({file_format.value}, {file_size} bytes) -> {document_id}")
        return metadata

    def process_document(self, document_id: str, content: bytes) -> ExtractedDocument:
        """Executes content extraction. Intended for background execution."""
        metadata = self._metadata_store.get(document_id)
        if not metadata:
            raise ResourceNotFoundException("Document", document_id)

        metadata.status = DocumentStatus.PROCESSING
        logger.info(f"Starting extraction for document {document_id} [{metadata.filename}]")

        try:
            extractor = get_extractor(metadata.file_format)
            extracted_doc = extractor.extract(content, metadata)

            # Update stores
            self._metadata_store[document_id] = extracted_doc.metadata
            self._document_store[document_id] = extracted_doc

            logger.info(
                f"Successfully extracted {document_id}: "
                f"{extracted_doc.metadata.total_pages} pages, {extracted_doc.metadata.total_characters} chars"
            )
            return extracted_doc

        except Exception as e:
            logger.error(f"Extraction failed for document {document_id}: {str(e)}")
            metadata.status = DocumentStatus.FAILED
            metadata.error_message = f"Extraction failure: {str(e)}"
            self._metadata_store[document_id] = metadata
            raise e

    def get_metadata(self, document_id: str) -> DocumentMetadata:
        """Retrieves document metadata by ID."""
        metadata = self._metadata_store.get(document_id)
        if not metadata:
            raise ResourceNotFoundException("Document", document_id)
        return metadata

    def get_extracted_document(self, document_id: str) -> ExtractedDocument:
        """Retrieves full extracted document text and pages."""
        doc = self._document_store.get(document_id)
        if not doc:
            metadata = self.get_metadata(document_id)
            if metadata.status == DocumentStatus.FAILED:
                raise ValidationException(f"Document extraction failed: {metadata.error_message}")
            raise ValidationException(f"Document is currently in '{metadata.status.value}' state; extraction not ready.")
        return doc

    def list_documents(self) -> List[DocumentMetadata]:
        """Lists all registered documents."""
        return list(self._metadata_store.values())


# Global singleton instance
ingestion_service = IngestionService()
