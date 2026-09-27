"""Mission Generator composing complete GameSpecification contracts for the Game Engine."""

from datetime import datetime, timezone
import uuid
from typing import Optional

from shared.schemas.game_specification import (
    ChallengePayload,
    GameSpecification,
    NarrativePayload,
    RewardPayload,
    SpecificationMetadata,
)
from app.knowledge.models import Concept
from app.generation.models import NPCPersona
from app.generation.npc_generator import npc_generator
from app.generation.question_generator import question_generator
from app.generation.boss_generator import boss_generator
from app.objectives.generator import objective_generator
from app.core.logging import get_logger

logger = get_logger("app.generation.mission_generator")


class MissionGenerator:
    """Orchestrates generation of complete, validated GameSpecification missions."""

    def generate_mission(
        self,
        concept: Concept,
        difficulty: int = 2,
        is_boss: bool = False,
        persona: NPCPersona = NPCPersona.ARCHMAGE_ALAN,
        document_id: Optional[str] = None,
    ) -> GameSpecification:
        """Constructs an end-to-end GameSpecification payload."""
        difficulty = max(1, min(5, difficulty))
        logger.info(f"Generating GameSpecification for concept='{concept.name}' (diff={difficulty}, is_boss={is_boss})")

        # 1. Generate learning objective
        obj = objective_generator.generate_for_difficulty(concept, difficulty)

        # 2. Generate narrative
        zone_themes = {
            1: "crystal_archives",
            2: "cyber_core",
            3: "quantum_conduit",
            4: "overclocked_forge",
            5: "singularity_rift",
        }
        theme = zone_themes.get(difficulty, "cyber_core")
        intro = (
            f"You have arrived at the {theme.replace('_', ' ').title()}. "
            f"The system bus is throttled by competing processes. "
            f"Your mission is to analyze and apply {concept.name} to stabilize the core."
        )
        narrative = NarrativePayload(
            zone_theme=theme,
            mission_intro=intro,
        )

        # 3. Generate NPC dialogue
        npc = npc_generator.generate_npc_payload(
            concept=concept,
            persona=persona,
            difficulty=difficulty,
        )

        # 4. Generate challenge & hints
        q = question_generator.generate_question(
            concept=concept,
            difficulty=difficulty,
            challenge_type="boss_override" if is_boss else "mcq",
        )
        challenge = ChallengePayload(
            challenge_id=q.challenge_id,
            challenge_type=q.challenge_type,
            prompt=q.prompt,
            options=q.options,
            correct_option_id=q.correct_option_id,
            hints=q.hints,
            explanation=q.explanation,
        )

        # 5. Generate boss payload if applicable
        boss = boss_generator.generate_boss_payload(
            concept=concept,
            is_boss_mission=is_boss,
            phases=2 if is_boss else 1,
        )

        # 6. Reward economics scaled to difficulty
        xp = 100 * difficulty if not is_boss else 250 * difficulty
        coins = 20 * difficulty if not is_boss else 50 * difficulty
        mastery_boost = min(0.3, 0.05 * difficulty)
        reward = RewardPayload(
            xp=xp,
            knowledge_coins=coins,
            mastery_boost_potential=round(mastery_boost, 2),
        )

        # 7. Metadata grounding
        mission_id = f"MSN-{concept.concept_id.upper()[:10]}-{uuid.uuid4().hex[:4].upper()}"
        metadata = SpecificationMetadata(
            source_document_id=document_id,
            chunk_ids=concept.source_chunk_ids,
            generated_at=datetime.now(timezone.utc).isoformat(),
            generator_model="arcana-ai-brain-v1",
        )

        # 8. Assemble full specification
        spec = GameSpecification(
            version="1.0.0",
            mission_id=mission_id,
            concept_id=concept.concept_id,
            title=f"Trial of {concept.name}: Level {difficulty}",
            difficulty=difficulty,
            learning_objective=obj.statement,
            narrative=narrative,
            npc=npc,
            challenge=challenge,
            boss=boss,
            reward=reward,
            metadata=metadata,
        )

        logger.info(f"Successfully generated validated GameSpecification: {spec.mission_id}")
        return spec


mission_generator = MissionGenerator()
