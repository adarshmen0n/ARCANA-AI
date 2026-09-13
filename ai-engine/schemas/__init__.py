"""Shared Pydantic Schemas for ARCANA AI Brain.

Provides typed, validated domain models for documents, concepts,
learning graphs, generation, game specifications, and personalization.
"""

from .base import ArcanaBaseModel, generate_id, current_utc_time
from .document import Section, ExtractedDocument, Chunk
from .knowledge import RelationshipType, Concept, Relationship, KnowledgeGraph
from .learning_graph import LearningGraphNode, LearningGraphEdge, LearningGraph, LearningSequence
from .generation import (
    QuestionType,
    GameMechanic,
    LearningObjective,
    Lesson,
    Question,
    Hint,
    Story,
    NPC,
    Reward,
    CompletionCondition,
    Mission,
    BossChallenge,
)
from .game_spec import Chapter, Campaign, GameSpecification
from .personalization import ActionType, ConceptMastery, StudentState, GameplayEvent, NextAction
from .job import JobStatus, ProcessingJob

__all__ = [
    "ArcanaBaseModel",
    "generate_id",
    "current_utc_time",
    "Section",
    "ExtractedDocument",
    "Chunk",
    "RelationshipType",
    "Concept",
    "Relationship",
    "KnowledgeGraph",
    "LearningGraphNode",
    "LearningGraphEdge",
    "LearningGraph",
    "LearningSequence",
    "QuestionType",
    "GameMechanic",
    "LearningObjective",
    "Lesson",
    "Question",
    "Hint",
    "Story",
    "NPC",
    "Reward",
    "CompletionCondition",
    "Mission",
    "BossChallenge",
    "Chapter",
    "Campaign",
    "GameSpecification",
    "ActionType",
    "ConceptMastery",
    "StudentState",
    "GameplayEvent",
    "NextAction",
    "JobStatus",
    "ProcessingJob",
]
