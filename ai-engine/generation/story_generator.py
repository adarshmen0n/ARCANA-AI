"""Story and Narrative Generator for ARCANA AI Brain."""

from schemas.knowledge import Concept
from schemas.generation import Story
from schemas.base import generate_id
from .base import BaseGenerator


class StoryGenerator(BaseGenerator):
    """Generates immersive pedagogical story context without altering educational truth."""

    def generate_story_context(self, concept: Concept, subject: str = "Arcana Realm") -> Story:
        return Story(
            story_id=generate_id("sty"),
            world=f"{subject} Citadel",
            context=(
                f"The archive sector governing {concept.name} has experienced memory drift. "
                f"Scholars require your analytical insight to restore the corrupted nodes."
            ),
            motivation=f"Mastering {concept.name} is vital to stabilizing the system and unlocking the inner sanctum.",
            mission_setting=f"Archive Vault of {concept.name}",
        )
