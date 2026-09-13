"""Game Specification contract for Dasarth's Game Engine.

This is the primary contract boundary between the ARCANA AI Brain
and the Game Systems Engine. Dasarth's engine receives pure structured data
and maps predefined mechanics without executing arbitrary code.
"""

from typing import Any, Dict, List, Optional
from pydantic import Field
from .base import ArcanaBaseModel, generate_id, current_utc_time
from .generation import Mission, BossChallenge, LearningObjective


class Chapter(ArcanaBaseModel):
    """An educational chapter grouping coherent objectives, missions, and boss assessment."""

    id: str = Field(default_factory=lambda: generate_id("chp"))
    title: str = Field(description="Chapter title")
    description: str = Field(default="")
    learning_objectives: List[LearningObjective] = Field(default_factory=list)
    missions: List[Mission] = Field(default_factory=list)
    boss: Optional[BossChallenge] = None


class Campaign(ArcanaBaseModel):
    """The overarching educational campaign spanning all chapters for a subject."""

    id: str = Field(default_factory=lambda: generate_id("cmp"))
    title: str = Field(description="Campaign title")
    subject: str = Field(description="Subject domain (e.g. Operating Systems, Python, Biology)")
    difficulty: int = Field(default=2, ge=1, le=5)
    chapters: List[Chapter] = Field(default_factory=list)


class GameSpecification(ArcanaBaseModel):
    """The root Game Specification Contract consumed by the Game Engine."""

    schema_version: str = Field(default="1.0", description="Immutable contract version")
    campaign: Campaign
    metadata: Dict[str, Any] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: current_utc_time().isoformat())
