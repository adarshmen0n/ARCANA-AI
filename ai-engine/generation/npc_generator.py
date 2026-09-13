"""NPC Generator producing structured pedagogical character dialogue."""

from schemas.knowledge import Concept
from schemas.generation import NPC
from schemas.base import generate_id
from .base import BaseGenerator


class NPCGenerator(BaseGenerator):
    """Generates educational NPCs acting as guides, mentors, or challenge keepers."""

    def generate_npc(self, concept: Concept) -> NPC:
        dialogue = [
            f"Greetings, seeker. Today we explore {concept.name}.",
            f"Pay careful attention: {concept.description[:120]}.",
            "Whenever you are ready, engage the simulation and test your understanding!",
        ]

        return NPC(
            npc_id=generate_id("npc"),
            name=f"Archivist of {concept.name}",
            role="Educational Mentor",
            educational_purpose=f"Guide the learner through foundational principles of {concept.name}.",
            tone="encouraging",
            dialogue=dialogue,
            concept_ids=[concept.concept_id],
        )
