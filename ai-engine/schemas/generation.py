"""Generation schemas: Lessons, Questions, Hints, Story, NPCs, Missions, Boss Challenges, and Rewards."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import Field
from .base import ArcanaBaseModel, generate_id


class QuestionType(str, Enum):
    """Question formats supported across ARCANA learning activities."""

    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    FILL_IN_THE_BLANK = "fill_in_the_blank"
    MATCHING = "matching"
    ORDERING = "ordering"
    SCENARIO_BASED = "scenario_based"
    APPLICATION_BASED = "application_based"


class GameMechanic(str, Enum):
    """Mechanics natively supported by Dasarth's Game Engine."""

    QUIZ = "quiz"
    MATCHING = "matching"
    ORDERING = "ordering"
    PUZZLE = "puzzle"
    EXPLORATION = "exploration"
    BOSS_FIGHT = "boss_fight"


class LearningObjective(ArcanaBaseModel):
    """Pedagogical goal anchoring every lesson, question, and mission."""

    objective_id: str = Field(default_factory=lambda: generate_id("obj"))
    concept_id: str = Field(description="Target concept ID")
    description: str = Field(description="Clear statement of what the learner will understand or perform")
    bloom_level: str = Field(default="understand", description="remember, understand, apply, analyze, evaluate, create")
    success_criteria: List[str] = Field(default_factory=list)


class Lesson(ArcanaBaseModel):
    """Structured educational lesson unit."""

    lesson_id: str = Field(default_factory=lambda: generate_id("lsn"))
    concept_id: str = Field(description="Concept being taught")
    learning_objective_id: Optional[str] = None
    title: str = Field(description="Lesson title")
    explanation: str = Field(description="Clear, grounded instructional text")
    examples: List[str] = Field(default_factory=list, description="Concrete examples illustrating the concept")
    key_points: List[str] = Field(default_factory=list, description="High-yield takeaways")
    analogy: Optional[str] = Field(default=None, description="Intuitive real-world analogy")
    source_references: List[str] = Field(default_factory=list, description="Source chunk IDs grounding this lesson")


class Question(ArcanaBaseModel):
    """Validated assessment question."""

    question_id: str = Field(default_factory=lambda: generate_id("qst"))
    concept_id: str = Field(description="Target concept ID")
    type: QuestionType = Field(default=QuestionType.MCQ)
    question: str = Field(description="The question prompt or problem statement")
    options: List[str] = Field(default_factory=list, description="Choices (empty for direct answer formats)")
    correct_answer: str = Field(description="Exact correct answer matching one of the options or value")
    explanation: str = Field(description="Explanation of why this answer is correct")
    difficulty: int = Field(default=2, ge=1, le=5)
    source_references: List[str] = Field(default_factory=list)


class Hint(ArcanaBaseModel):
    """Progressive scaffolding hint."""

    hint_id: str = Field(default_factory=lambda: generate_id("hnt"))
    question_id: Optional[str] = None
    tier: int = Field(ge=1, le=4, description="1=Reminder, 2=Directional, 3=Strong clue, 4=Near-answer")
    text: str = Field(description="The hint content")


class Story(ArcanaBaseModel):
    """Narrative wrapper providing contextual motivation without altering facts."""

    story_id: str = Field(default_factory=lambda: generate_id("sty"))
    world: str = Field(default="Arcana Realm")
    context: str = Field(description="Narrative context surrounding the mission")
    motivation: str = Field(description="Why the player needs to solve this educational problem")
    mission_setting: str = Field(default="Knowledge Archive")


class NPC(ArcanaBaseModel):
    """Non-Player Character acting as an educational guide or challenger."""

    npc_id: str = Field(default_factory=lambda: generate_id("npc"))
    name: str = Field(description="Name of the guide or character")
    role: str = Field(description="e.g. Mentor, Archivist, Challenge Keeper")
    educational_purpose: str = Field(description="What pedagogical task this NPC fulfills")
    tone: str = Field(default="encouraging", description="encouraging, analytical, mysterious, challenging")
    dialogue: List[str] = Field(default_factory=list, description="Concise dialogue lines")
    concept_ids: List[str] = Field(default_factory=list)


class Reward(ArcanaBaseModel):
    """Game progression reward."""

    xp: int = Field(default=50, ge=0)
    coins: int = Field(default=10, ge=0)
    badge_id: Optional[str] = None
    achievement_name: Optional[str] = None


class CompletionCondition(ArcanaBaseModel):
    """Deterministic game completion rule."""

    type: str = Field(default="min_accuracy", description="min_accuracy, all_correct, speed_threshold")
    target_metric: str = Field(default="accuracy")
    required_value: float = Field(default=0.7, description="Threshold required for victory")


class Mission(ArcanaBaseModel):
    """Complete game-ready educational mission."""

    mission_id: str = Field(default_factory=lambda: generate_id("msn"))
    title: str = Field(description="Mission title")
    concept_ids: List[str] = Field(description="Concepts taught or tested")
    learning_objective: str = Field(description="Pedagogical objective")
    mechanic: GameMechanic = Field(description="Predefined game engine mechanic")
    challenge: Dict[str, Any] = Field(default_factory=dict, description="Mechanic-specific structured data")
    difficulty: int = Field(default=2, ge=1, le=5)
    story: Optional[Story] = None
    npc: Optional[NPC] = None
    questions: List[Question] = Field(default_factory=list)
    hints: List[Hint] = Field(default_factory=list)
    rewards: Reward = Field(default_factory=Reward)
    completion_condition: CompletionCondition = Field(default_factory=CompletionCondition)
    source_references: List[str] = Field(default_factory=list)


class BossChallenge(ArcanaBaseModel):
    """Capstone multi-concept assessment challenge."""

    boss_id: str = Field(default_factory=lambda: generate_id("boss"))
    name: str = Field(description="Boss entity or challenge name")
    concept_ids: List[str] = Field(description="All cumulative concepts tested")
    narrative_intro: str = Field(description="Dramatic educational context")
    phases: List[Dict[str, Any]] = Field(default_factory=list, description="Stages of the boss encounter")
    questions: List[Question] = Field(default_factory=list)
    rewards: Reward = Field(default_factory=lambda: Reward(xp=200, coins=50, achievement_name="Chapter Master"))
    completion_condition: CompletionCondition = Field(default_factory=lambda: CompletionCondition(required_value=0.8))
