"""Data models for Student interactions and behavioral metrics."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class StudentInteractionRecord(BaseModel):
    interaction_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique interaction UUID",
    )
    student_id: str = Field(..., description="Student identifier")
    concept_id: str = Field(..., description="Concept attempted")
    difficulty: int = Field(default=2, ge=1, le=5, description="Difficulty of challenge (1-5)")
    is_correct: bool = Field(..., description="Whether response was correct")
    time_taken_seconds: float = Field(default=0.0, ge=0.0, description="Response time in seconds")
    hints_used: int = Field(default=0, ge=0, description="Total hints viewed")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp",
    )
