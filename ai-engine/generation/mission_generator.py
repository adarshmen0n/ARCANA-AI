"""Mission Generator: Synthesizes learning objectives into game-ready missions."""

from typing import List, Optional
from schemas.knowledge import Concept
from schemas.generation import (
    Mission,
    GameMechanic,
    Reward,
    CompletionCondition,
    LearningObjective,
)
from schemas.base import generate_id
from .base import BaseGenerator
from .objective_generator import ObjectiveGenerator
from .question_generator import QuestionGenerator
from .hint_generator import HintGenerator
from .story_generator import StoryGenerator
from .npc_generator import NPCGenerator


class MissionGenerator(BaseGenerator):
    """Generates structured educational missions for Dasarth's Game Engine."""

    def __init__(self, provider_router):
        super().__init__(provider_router)
        self.objective_gen = ObjectiveGenerator(provider_router)
        self.question_gen = QuestionGenerator(provider_router)
        self.hint_gen = HintGenerator(provider_router)
        self.story_gen = StoryGenerator(provider_router)
        self.npc_gen = NPCGenerator(provider_router)

    def generate_mission(
        self,
        concept: Concept,
        objective: Optional[LearningObjective] = None,
        mechanic: GameMechanic = GameMechanic.QUIZ,
    ) -> Mission:
        # Step 1: Ensure learning objective exists
        obj = objective or self.objective_gen.generate_objective(concept)

        # Step 2: Generate assessment questions
        questions = self.question_gen.generate_questions_for_concept(concept, count=2)

        # Step 3: Generate progressive hints for questions
        hints = []
        for q in questions:
            hints.extend(self.hint_gen.generate_progressive_hints(q))

        # Step 4: Generate story immersion & NPC
        story = self.story_gen.generate_story_context(concept)
        npc = self.npc_gen.generate_npc(concept)

        # Step 5: Reward and completion criteria
        rewards = Reward(
            xp=50 * concept.difficulty,
            coins=10 * concept.difficulty,
            achievement_name=f"{concept.name} Initiate",
        )
        completion_condition = CompletionCondition(
            type="min_accuracy",
            target_metric="accuracy",
            required_value=0.7,
        )

        challenge = {
            "mechanic_type": mechanic.value,
            "target_concept": concept.name,
            "time_limit_seconds": 120,
        }

        return Mission(
            mission_id=generate_id("msn"),
            title=f"Trial of {concept.name}",
            concept_ids=[concept.concept_id],
            learning_objective=obj.description,
            mechanic=mechanic,
            challenge=challenge,
            difficulty=concept.difficulty,
            story=story,
            npc=npc,
            questions=questions,
            hints=hints,
            rewards=rewards,
            completion_condition=completion_condition,
            source_references=concept.source_chunk_ids,
        )
