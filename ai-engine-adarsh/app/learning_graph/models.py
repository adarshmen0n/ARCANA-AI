"""Data models for Learning Graph representation and adaptive path planning."""

from typing import List, Optional
from pydantic import BaseModel, Field


class LearningNode(BaseModel):
    concept_id: str = Field(..., description="Unique concept key")
    name: str = Field(..., description="Concept display name")
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty level (1-5)")
    topic: str = Field(..., description="Curriculum domain/topic")
    prerequisites: List[str] = Field(default_factory=list, description="Direct prerequisite concept IDs")
    dependents: List[str] = Field(default_factory=list, description="Subsequent dependent concept IDs")


class LearningPath(BaseModel):
    path_id: str = Field(..., description="Unique learning path identifier")
    document_id: str = Field(..., description="Source document identifier")
    ordered_concept_ids: List[str] = Field(..., description="Topologically sorted sequence of concepts")
    total_nodes: int = Field(..., ge=0, description="Number of concepts in path")
    nodes: List[LearningNode] = Field(..., description="Full node metadata in topological order")


class NextConceptRecommendation(BaseModel):
    recommended_concept: LearningNode = Field(..., description="The next optimal concept to learn")
    reason: str = Field(..., description="Pedagogical rationale for this recommendation")
    prerequisites_satisfied: bool = Field(default=True, description="Whether all prerequisites are completed")
    is_remediation: bool = Field(default=False, description="Flag if recommendation is a remedial review")
    alternative_ready_concepts: List[str] = Field(
        default_factory=list, description="Other concepts currently unlocked for learning"
    )
