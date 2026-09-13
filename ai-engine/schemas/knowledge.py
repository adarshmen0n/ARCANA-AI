"""Knowledge schemas: Concepts, Relationships, and Knowledge Graphs."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import Field
from .base import ArcanaBaseModel, generate_id


class RelationshipType(str, Enum):
    """Educational relationship types supported by the ARCANA Knowledge Engine."""

    PREREQUISITE_OF = "prerequisite_of"
    DEPENDS_ON = "depends_on"
    PART_OF = "part_of"
    CONTAINS = "contains"
    EXAMPLE_OF = "example_of"
    SIMILAR_TO = "similar_to"
    CONTRASTS_WITH = "contrasts_with"
    FOLLOWS = "follows"
    RELATED_TO = "related_to"


class Concept(ArcanaBaseModel):
    """Structured educational concept identified by the Knowledge Engine."""

    concept_id: str = Field(default_factory=lambda: generate_id("cpt"))
    name: str = Field(description="Name or title of the concept")
    description: str = Field(description="Clear educational definition or explanation")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Pedagogical importance (0.0 to 1.0)")
    difficulty: int = Field(default=1, ge=1, le=5, description="Intrinsic content difficulty (1=Beginner to 5=Expert)")
    parent_topic_id: Optional[str] = Field(default=None, description="Optional parent topic or chapter ID")
    prerequisite_ids: List[str] = Field(default_factory=list, description="List of concept IDs required beforehand")
    source_chunk_ids: List[str] = Field(default_factory=list, description="Traceable chunk IDs grounding this concept")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Relationship(ArcanaBaseModel):
    """Pedagogical relationship connecting two concepts."""

    relationship_id: str = Field(default_factory=lambda: generate_id("rel"))
    from_concept_id: str = Field(description="Source concept ID")
    to_concept_id: str = Field(description="Target concept ID")
    relationship: RelationshipType = Field(description="Type of relationship")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Validation confidence score")
    source_chunk_ids: List[str] = Field(default_factory=list, description="Grounding chunks supporting this edge")


class KnowledgeGraph(ArcanaBaseModel):
    """Complete structured knowledge representation of ingested content."""

    subject: str = Field(default="General", description="Subject area (e.g. Operating Systems, Python)")
    document_id: str = Field(description="Source document ID")
    concepts: List[Concept] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
