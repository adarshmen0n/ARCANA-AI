"""ARCANA-AI Shared Schemas Package.

Contains canonical Pydantic models for cross-module contracts.
"""

from .game_specification import (
    GameSpecification,
    NarrativePayload,
    NPCPayload,
    ChallengeOption,
    ProgressiveHint,
    ChallengePayload,
    BossPayload,
    RewardPayload,
    SpecificationMetadata,
)
from .game_event import GameEvent, GameEventType, EventPayload
from .student_mastery import StudentProfile, ConceptMastery, MasteryUpdateResult

__all__ = [
    "GameSpecification",
    "NarrativePayload",
    "NPCPayload",
    "ChallengeOption",
    "ProgressiveHint",
    "ChallengePayload",
    "BossPayload",
    "RewardPayload",
    "SpecificationMetadata",
    "GameEvent",
    "GameEventType",
    "EventPayload",
    "StudentProfile",
    "ConceptMastery",
    "MasteryUpdateResult",
]
