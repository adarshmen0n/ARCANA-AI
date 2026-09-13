"""Multi-tier validation engine for educational artifacts and Game Specifications."""

import logging
import re
from typing import List, Optional, Set
from schemas.base import ArcanaBaseModel
from schemas.game_spec import GameSpecification
from schemas.generation import GameMechanic, QuestionType

logger = logging.getLogger("arcana.validation")


class ValidationReport(ArcanaBaseModel):
    """Structured report detailing validation findings across tiers."""

    is_valid: bool
    tier_passed: str
    errors: List[str]
    warnings: List[str]


class ValidationEngine:
    """Enforces multi-tier validation to ensure invalid or unsafe output never reaches the Game Engine."""

    # Prohibited patterns to enforce Section 35: NO ARBITRARY CODE
    CODE_INJECTION_PATTERNS = [
        re.compile(r"\b(?:eval|exec|os\.system|subprocess|__import__)\s*\(", re.IGNORECASE),
        re.compile(r"<script.*?>.*?</script>", re.IGNORECASE),
        re.compile(r"javascript:", re.IGNORECASE),
    ]

    @classmethod
    def validate_game_specification(
        cls,
        spec: GameSpecification,
        valid_concept_ids: Optional[Set[str]] = None,
    ) -> ValidationReport:
        errors: List[str] = []
        warnings: List[str] = []

        # Tier 1: Schema Version
        if spec.schema_version != "1.0":
            errors.append(f"Invalid schema_version '{spec.schema_version}'. Expected '1.0'.")

        # Tier 2: Campaign and Chapters integrity
        campaign = spec.campaign
        if not campaign.title.strip():
            errors.append("Campaign title is empty.")
        if not campaign.chapters:
            errors.append("Campaign must contain at least one chapter.")

        for chp_idx, chapter in enumerate(campaign.chapters):
            if not chapter.missions and not chapter.boss:
                errors.append(f"Chapter '{chapter.title}' (index {chp_idx}) has neither missions nor boss.")

            # Tier 3: Missions and Question validation
            for m_idx, mission in enumerate(chapter.missions):
                # Check mechanic validity
                if not isinstance(mission.mechanic, GameMechanic):
                    errors.append(f"Mission '{mission.title}' has invalid mechanic: {mission.mechanic}")

                # Check referential integrity of concepts
                if valid_concept_ids:
                    for cid in mission.concept_ids:
                        if cid not in valid_concept_ids:
                            errors.append(
                                f"Mission '{mission.title}' references non-existent concept_id '{cid}'."
                            )

                # Check completion conditions
                if mission.completion_condition.required_value <= 0.0:
                    errors.append(
                        f"Mission '{mission.title}' has invalid completion threshold: {mission.completion_condition.required_value}"
                    )

                # Validate Questions
                for q_idx, q in enumerate(mission.questions):
                    if not q.question.strip():
                        errors.append(f"Mission '{mission.title}' question #{q_idx} is empty.")

                    # MCQ / TrueFalse answer key validation
                    if q.type in {QuestionType.MCQ, QuestionType.TRUE_FALSE}:
                        if not q.options:
                            errors.append(f"Question '{q.question_id}' of type {q.type} has no options.")
                        elif q.correct_answer not in q.options:
                            errors.append(
                                f"Question '{q.question_id}' correct_answer '{q.correct_answer}' not found in options."
                            )

                # Tier 4: Security & Arbitrary code prevention
                all_text_blobs = [
                    mission.title,
                    mission.learning_objective,
                    str(mission.challenge),
                ]
                if mission.story:
                    all_text_blobs.extend([mission.story.context, mission.story.motivation])
                if mission.npc:
                    all_text_blobs.extend(mission.npc.dialogue)

                for blob in all_text_blobs:
                    for pattern in cls.CODE_INJECTION_PATTERNS:
                        if pattern.search(blob):
                            errors.append(f"Prohibited executable code pattern detected in mission '{mission.title}'.")

        is_valid = len(errors) == 0
        tier = "Approved (All Tiers Passed)" if is_valid else "Rejected"
        if not is_valid:
            logger.error("Validation failed with %d errors: %s", len(errors), "; ".join(errors))

        return ValidationReport(
            is_valid=is_valid,
            tier_passed=tier,
            errors=errors,
            warnings=warnings,
        )
