"""Data models for ARCANA generation subsystems (Lessons, Questions, Hints, NPCs, Bosses, Missions)."""

from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

from shared.schemas.game_specification import (
    ChallengeOption,
    ProgressiveHint,
    NPCPayload,
    NarrativePayload,
    BossPayload,
    RewardPayload,
    GameSpecification,
)
from app.objectives.models import BloomTaxonomyLevel


class NPCPersona(str, Enum):
    ARCHMAGE_ALAN = "archmage_alan"
    CHRONOS_WARDEN = "chronos_warden"
    GLITCH_SPRITE = "glitch_sprite"
    VOID_SENTINEL = "void_sentinel"


class Lesson(BaseModel):
    concept_id: str = Field(..., description="Target concept ID")
    concept_name: str = Field(..., description="Display concept name")
    title: str = Field(..., description="Engaging lesson title")
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty rating")
    story_hook: str = Field(..., description="Narrative or real-world hook captivating the student")
    core_explanation: str = Field(..., description="Rigorous educational explanation")
    analogy: str = Field(..., description="Intuitive real-world or game world analogy")
    key_takeaways: List[str] = Field(..., min_length=1, description="Bulleted takeaway points")
    common_misconceptions: List[str] = Field(default_factory=list, description="Common misunderstandings addressed")
    source_chunks: List[str] = Field(default_factory=list, description="Grounding source chunk IDs")


class GeneratedQuestion(BaseModel):
    challenge_id: str = Field(..., description="Unique question identifier")
    concept_id: str = Field(..., description="Concept tested")
    bloom_level: BloomTaxonomyLevel = Field(..., description="Bloom taxonomy level")
    difficulty: int = Field(..., ge=1, le=5, description="Difficulty (1-5)")
    challenge_type: Literal["mcq", "concept_puzzle", "boss_override", "calculation"] = Field(
        default="mcq", description="Interaction format"
    )
    prompt: str = Field(..., min_length=5, description="Question stem")
    options: List[ChallengeOption] = Field(..., min_length=2, max_length=6, description="Multiple choice options")
    correct_option_id: str = Field(..., description="ID matching correct option")
    hints: List[ProgressiveHint] = Field(default_factory=list, description="Tier 1-3 progressive hints")
    explanation: str = Field(..., min_length=5, description="Pedagogical explanation of why correct option is right")
    distractor_explanations: Optional[dict] = Field(default_factory=dict, description="Explanation for each distractor")


class BossEncounter(BaseModel):
    boss_id: str
    boss_name: str
    title: str
    lore: str
    hp: int = Field(default=100, ge=1)
    phases: int = Field(default=1, ge=1, le=5)
    shield_weakness_concept: str
    challenges: List[GeneratedQuestion]
