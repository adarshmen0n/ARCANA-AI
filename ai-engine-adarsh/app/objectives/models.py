"""Data models for Learning Objectives and Bloom's Taxonomy."""

from enum import Enum
from typing import List, Optional
import uuid
from pydantic import BaseModel, Field


class BloomTaxonomyLevel(str, Enum):
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"


class LearningObjective(BaseModel):
    objective_id: str = Field(
        default_factory=lambda: f"obj_{uuid.uuid4().hex[:8]}",
        description="Unique objective identifier",
    )
    concept_id: str = Field(..., description="Target concept identifier")
    bloom_level: BloomTaxonomyLevel = Field(..., description="Cognitive taxonomy level")
    difficulty: int = Field(default=2, ge=1, le=5, description="Associated challenge difficulty (1-5)")
    statement: str = Field(..., description="Measurable behavioral learning objective statement")
    action_verbs: List[str] = Field(default_factory=list, description="Action verbs from Bloom taxonomy")
    success_criteria: str = Field(..., description="Measurable indicator of mastery for this objective")


class ConceptObjectivesResult(BaseModel):
    concept_id: str
    concept_name: str
    objectives: List[LearningObjective]
    total_objectives: int
