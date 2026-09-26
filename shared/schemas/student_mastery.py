"""Student Mastery & Learner Profile Pydantic Schema.

Defines the structure for tracking student mastery, learning history, and adaptive progression.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ConceptMastery(BaseModel):
    concept_id: str = Field(..., description="Unique concept key")
    mastery_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Mastery score between 0.0 and 1.0")
    total_attempts: int = Field(default=0, ge=0, description="Total questions/challenges attempted")
    successful_attempts: int = Field(default=0, ge=0, description="Total successful attempts")
    consecutive_correct: int = Field(default=0, ge=0, description="Consecutive correct answers")
    last_attempt_timestamp: Optional[str] = Field(None, description="ISO timestamp of last activity")
    last_difficulty_solved: int = Field(default=1, ge=1, le=5, description="Highest difficulty successfully solved")


class StudentProfile(BaseModel):
    student_id: str = Field(..., description="Unique learner identifier")
    display_name: str = Field(default="Learner", description="Student display name")
    xp: int = Field(default=0, ge=0, description="Accumulated experience points")
    level: int = Field(default=1, ge=1, description="Current player level")
    knowledge_coins: int = Field(default=0, ge=0, description="Knowledge coins in inventory")
    concept_mastery: Dict[str, ConceptMastery] = Field(
        default_factory=dict, description="Map of concept_id to mastery record"
    )
    completed_missions: List[str] = Field(default_factory=list, description="IDs of successfully finished missions")
    weak_concepts: List[str] = Field(default_factory=list, description="Concepts flagged for remediation")
    strong_concepts: List[str] = Field(default_factory=list, description="Concepts with mastery >= 0.8")


class MasteryUpdateResult(BaseModel):
    student_id: str = Field(..., description="Target student ID")
    concept_id: str = Field(..., description="Concept updated")
    previous_score: float = Field(..., ge=0.0, le=1.0)
    new_score: float = Field(..., ge=0.0, le=1.0)
    score_delta: float = Field(..., description="Delta change in mastery score")
    remediation_required: bool = Field(default=False, description="Flag if score drop triggers remediation")
    suggested_next_difficulty: int = Field(default=2, ge=1, le=5)
