"""Async job lifecycle and task tracking schemas."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import Field
from .base import ArcanaBaseModel, generate_id, current_utc_time


class JobStatus(str, Enum):
    """Lifecycle status of background document processing pipelines."""

    QUEUED = "QUEUED"
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    GENERATING = "GENERATING"
    VALIDATING = "VALIDATING"
    READY = "READY"
    FAILED = "FAILED"


class ProcessingJob(ArcanaBaseModel):
    """Tracks asynchronous processing jobs for long-running document compilation."""

    job_id: str = Field(default_factory=lambda: generate_id("job"))
    document_id: Optional[str] = None
    status: JobStatus = Field(default=JobStatus.QUEUED)
    progress_percent: int = Field(default=0, ge=0, le=100)
    current_stage: str = Field(default="Enqueued")
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: current_utc_time().isoformat())
    updated_at: str = Field(default_factory=lambda: current_utc_time().isoformat())
