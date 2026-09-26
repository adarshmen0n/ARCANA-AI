"""GameEvent Pydantic Schema.

Defines the telemetry payload emitted by the Game Engine and processed by the AI Engine.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class GameEventType(str, Enum):
    QUESTION_STARTED = "QUESTION_STARTED"
    QUESTION_ANSWERED = "QUESTION_ANSWERED"
    HINT_REQUESTED = "HINT_REQUESTED"
    MISSION_STARTED = "MISSION_STARTED"
    MISSION_COMPLETED = "MISSION_COMPLETED"
    MISSION_FAILED = "MISSION_FAILED"
    NPC_INTERACTION = "NPC_INTERACTION"
    BOSS_STARTED = "BOSS_STARTED"
    BOSS_COMPLETED = "BOSS_COMPLETED"
    PLAYER_DIED = "PLAYER_DIED"


class EventPayload(BaseModel):
    challenge_id: Optional[str] = Field(None, description="Active challenge ID if applicable")
    selected_option_id: Optional[str] = Field(None, description="Option selected by player (e.g. A, B)")
    is_correct: Optional[bool] = Field(None, description="Whether submitted answer was correct")
    difficulty: int = Field(default=3, ge=1, le=5, description="Difficulty of the attempted challenge")
    time_taken_seconds: float = Field(default=0.0, ge=0.0, description="Time spent before action")
    hints_used_count: int = Field(default=0, ge=0, description="Total hints viewed during this challenge")
    highest_hint_level: int = Field(default=0, ge=0, le=3, description="Highest hint level accessed (0-3)")
    remaining_player_health: int = Field(default=100, ge=0, description="Current player health points")
    attempt_number: int = Field(default=1, ge=1, description="Attempt count for this challenge")


class GameEvent(BaseModel):
    version: str = Field(default="1.0.0", description="Schema version")
    event_id: str = Field(..., min_length=1, description="Unique event UUID v4")
    student_id: str = Field(..., min_length=1, description="Student/Learner identifier")
    session_id: str = Field(..., min_length=1, description="Game session identifier")
    mission_id: str = Field(..., min_length=1, description="Associated mission ID")
    concept_id: str = Field(..., min_length=1, description="Educational concept identifier")
    event_type: GameEventType = Field(..., description="Category of game telemetry event")
    payload: EventPayload = Field(default_factory=EventPayload, description="Detailed interaction telemetry")
    client_timestamp: str = Field(..., description="ISO 8601 UTC timestamp recorded by game client")
