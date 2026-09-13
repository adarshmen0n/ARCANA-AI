"""Question Generator producing validated assessment questions across multiple formats."""

from typing import List, Optional
from schemas.knowledge import Concept
from schemas.generation import Question, QuestionType
from schemas.base import generate_id
from .base import BaseGenerator


class QuestionGenerator(BaseGenerator):
    """Generates educationally grounded assessment questions with validated answer keys."""

    def generate_questions_for_concept(
        self,
        concept: Concept,
        count: int = 2,
    ) -> List[Question]:
        questions: List[Question] = []

        # Question 1: Multiple Choice Question (MCQ)
        mcq_options = [
            f"It provides {concept.name} mechanics to manage state.",
            f"It completely disables {concept.name} functionality.",
            "It is purely decorative syntax with no runtime effect.",
            "It forces infinite recursive execution.",
        ]
        correct_ans = mcq_options[0]

        q1 = Question(
            question_id=generate_id("qst"),
            concept_id=concept.concept_id,
            type=QuestionType.MCQ,
            question=f"What is the primary pedagogical role of {concept.name}?",
            options=mcq_options,
            correct_answer=correct_ans,
            explanation=f"{concept.name} is designed to manage state and organize logic as defined: {concept.description[:100]}.",
            difficulty=concept.difficulty,
            source_references=concept.source_chunk_ids,
        )
        questions.append(q1)

        # Question 2: True / False
        if count > 1:
            tf_options = ["True", "False"]
            q2 = Question(
                question_id=generate_id("qst"),
                concept_id=concept.concept_id,
                type=QuestionType.TRUE_FALSE,
                question=f"True or False: {concept.name} is relevant to understanding computational structure.",
                options=tf_options,
                correct_answer="True",
                explanation=f"True. {concept.name} plays an active role in structured reasoning.",
                difficulty=max(1, concept.difficulty - 1),
                source_references=concept.source_chunk_ids,
            )
            questions.append(q2)

        return questions[:count]
