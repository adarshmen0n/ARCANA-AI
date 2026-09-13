"""Boss Challenge Generator: Cumulative capstone assessments."""

from typing import List
from schemas.knowledge import Concept
from schemas.generation import BossChallenge, Question, Reward, CompletionCondition
from schemas.base import generate_id
from .base import BaseGenerator
from .question_generator import QuestionGenerator


class BossGenerator(BaseGenerator):
    """Generates cumulative chapter boss challenges testing integrated concepts."""

    def __init__(self, provider_router):
        super().__init__(provider_router)
        self.question_gen = QuestionGenerator(provider_router)

    def generate_boss_challenge(
        self,
        chapter_title: str,
        cumulative_concepts: List[Concept],
    ) -> BossChallenge:
        concept_ids = [c.concept_id for c in cumulative_concepts]
        names = ", ".join(c.name for c in cumulative_concepts[:3])

        # Generate capstone questions spanning multiple concepts
        all_questions: List[Question] = []
        for c in cumulative_concepts:
            all_questions.extend(self.question_gen.generate_questions_for_concept(c, count=1))

        phases = [
            {
                "phase_number": 1,
                "title": "Foundation Test",
                "description": f"Demonstrate baseline comprehension of {names}.",
                "question_indices": [0],
            },
            {
                "phase_number": 2,
                "title": "Synthesis Trial",
                "description": "Solve multi-concept dependencies and edge cases.",
                "question_indices": list(range(1, len(all_questions))),
            },
        ]

        rewards = Reward(
            xp=250,
            coins=75,
            badge_id="badge_chapter_master",
            achievement_name=f"Vanquisher of {chapter_title}",
        )

        return BossChallenge(
            boss_id=generate_id("boss"),
            name=f"Guardian of {chapter_title}",
            concept_ids=concept_ids,
            narrative_intro=(
                f"The Guardian challenges your mastery of {chapter_title}! "
                "Only those who understand the intricate connections between these concepts shall prevail."
            ),
            phases=phases,
            questions=all_questions,
            rewards=rewards,
            completion_condition=CompletionCondition(required_value=0.8),
        )
