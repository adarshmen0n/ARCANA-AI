"""Data models for Knowledge Engine concepts and semantic relationships."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    PREREQUISITE_OF = "prerequisite_of"
    DEPENDS_ON = "depends_on"
    PART_OF = "part_of"
    CONTAINS = "contains"
    EXAMPLE_OF = "example_of"
    SIMILAR_TO = "similar_to"
    CONTRASTS_WITH = "contrasts_with"
    FOLLOWS = "follows"
    CAUSES = "causes"
    REQUIRES = "requires"


class Concept(BaseModel):
    concept_id: str = Field(..., description="Unique machine key, e.g. cpu_scheduling_fcfs")
    name: str = Field(..., description="Human-readable concept name")
    topic: str = Field(..., description="Parent topic/domain, e.g. CPU Scheduling")
    definition: str = Field(..., description="Precise educational definition")
    difficulty: int = Field(default=2, ge=1, le=5, description="Difficulty rating (1=Very Easy, 5=Very Hard)")
    importance: float = Field(default=0.8, ge=0.0, le=1.0, description="Pedagogical importance score")
    examples: List[str] = Field(default_factory=list, description="Concrete examples or scenarios")
    common_misconceptions: List[str] = Field(default_factory=list, description="Documented student misconceptions")
    source_chunk_ids: List[str] = Field(default_factory=list, description="Grounding chunks where concept was discovered")


class ConceptRelationship(BaseModel):
    source_concept_id: str = Field(..., description="Subject concept ID")
    relationship_type: RelationshipType = Field(..., description="Semantic dependency type")
    target_concept_id: str = Field(..., description="Object concept ID")
    description: Optional[str] = Field(None, description="Explanation of why this relationship exists")


class KnowledgeExtractionResult(BaseModel):
    document_id: str
    concepts: List[Concept]
    relationships: List[ConceptRelationship]
    total_concepts: int
    total_relationships: int
