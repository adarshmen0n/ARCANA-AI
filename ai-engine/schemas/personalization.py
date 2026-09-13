"""Personalization, Mastery, and Adaptive Learning schemas."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import Field
from .base import ArcanaBaseModel, generate_id, current_utc_time


class ActionType(str, Enum):
    """Pedagogical next action determined by the adaptive loop."""

    LEARN = "learn"
    PRACTICE = "practice"
    REVISION = "revision"
    BOSS = "boss"
    ADVANCE = "advance"


class ConceptMastery(ArcanaBaseModel):
    """Dynamic mastery tracking for an individual concept."""

    concept_id: str
    mastery_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Pedagogical mastery (0.0 to 1.0)")
    attempts: int = Field(default=0, ge=0)
    correct_attempts: int = Field(default=0, ge=0)
    hints_used: int = Field(default=0, ge=0)
    avg_response_time_seconds: float = Field(default=0.0, ge=0.0)
    last_attempted: Optional[str] = None


class StudentState(ArcanaBaseModel):
    """State of the learner across all concepts, missions, and progression."""

    student_id: str
    current_level: int = Field(default=1, ge=1)
    total_xp: int = Field(default=0, ge=0)
    total_coins: int = Field(default=0, ge=0)
    masteries: Dict[str, ConceptMastery] = Field(default_factory=dict)
    completed_mission_ids: List[str] = Field(default_factory=list)
    weak_concept_ids: List[str] = Field(default_factory=list)
    last_updated: str = Field(default_factory=lambda: current_utc_time().isoformat())


class GameplayEvent(ArcanaBaseModel):
    """Analytics event emitted by the Game Engine after a player action or mission."""

    event_id: str = Field(default_factory=lambda: generate_id("evt"))
    student_id: str
    mission_id: str
    concept_id: str
    is_correct: bool
    hints_used: int = Field(default=0, ge=0)
    response_time_seconds: float = Field(default=5.0, ge=0.0)
    timestamp: str = Field(default_factory=lambda: current_utc_time().isoformat())


class NextAction(ArcanaBaseModel):
    """Adaptive recommendation for the next learning step."""

    action_type: ActionType
    recommended_concept_id: str
    recommended_mission_id: Optional[str] = None
    target_difficulty: int = Field(default=2, ge=1, le=5)
    hint_intensity: str = Field(default="standard", description="gentle, standard, high_scaffolding")
    explanation_level: str = Field(default="standard", description="simplified, standard, advanced")
    rationale: str = Field(description="Deterministic pedagogical rationale behind this decision")
