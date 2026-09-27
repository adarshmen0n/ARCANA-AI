"""Boss Encounter Generator creating multi-phase summative evaluation battles."""

from typing import List, Optional
from shared.schemas.game_specification import BossPayload
from app.knowledge.models import Concept
from app.generation.models import BossEncounter, GeneratedQuestion
from app.generation.question_generator import question_generator
from app.core.logging import get_logger

logger = get_logger("app.generation.boss_generator")


class BossGenerator:
    """Generates summative boss battles testing synthesis across prerequisite concepts."""

    @staticmethod
    def generate_boss_payload(
        concept: Concept,
        is_boss_mission: bool = True,
        phases: int = 2,
    ) -> BossPayload:
        """Constructs a BossPayload adhering to shared game contracts."""
        if not is_boss_mission:
            return BossPayload(is_boss_mission=False)

        c_id = concept.concept_id.lower()
        if "fcfs" in c_id or "first-come" in c_id:
            boss_id = "convoy_dragon"
            boss_name = "Ignis the Convoy Behemoth"
        elif "round_robin" in c_id:
            boss_id = "quantum_reaper"
            boss_name = "Slices the Quantum Reaper"
        elif "priority" in c_id:
            boss_id = "starvation_wraith"
            boss_name = "Vesper the Starvation Wraith"
        elif "deadlock" in c_id:
            boss_id = "deadlock_colossus"
            boss_name = "Malok the Deadlock Colossus"
        else:
            boss_id = f"boss_{concept.concept_id[:12]}"
            boss_name = f"Titan of {concept.name}"

        return BossPayload(
            is_boss_mission=True,
            boss_id=boss_id,
            boss_name=boss_name,
            shield_weakness_concept=concept.concept_id,
            phases=max(1, min(5, phases)),
        )

    def generate_full_encounter(
        self,
        concept: Concept,
        phases: int = 3,
    ) -> BossEncounter:
        """Generates a complete multi-phase Boss Encounter with challenges for each phase."""
        payload = self.generate_boss_payload(concept, is_boss_mission=True, phases=phases)

        encounter_challenges: List[GeneratedQuestion] = []
        for phase_idx in range(1, phases + 1):
            difficulty = min(5, 2 + phase_idx)
            challenge = question_generator.generate_question(
                concept=concept,
                difficulty=difficulty,
                challenge_type="boss_override",
            )
            challenge.prompt = f"[Phase {phase_idx}/{phases} - Boss Defense Override]: {challenge.prompt}"
            encounter_challenges.append(challenge)

        return BossEncounter(
            boss_id=payload.boss_id or "boss_unknown",
            boss_name=payload.boss_name or "Unknown Titan",
            title=f"Trial of the Ancients: Overcoming {payload.boss_name}",
            lore=f"The ancient guardian of {concept.topic} manifests. Its shield can only be breached using {concept.name}.",
            hp=100 * phases,
            phases=phases,
            shield_weakness_concept=concept.concept_id,
            challenges=encounter_challenges,
        )


boss_generator = BossGenerator()
