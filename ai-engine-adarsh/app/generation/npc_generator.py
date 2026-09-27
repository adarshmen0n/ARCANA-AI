"""NPC Generator producing immersive narrative dialogues and lore snippets."""

from typing import List, Optional
from shared.schemas.game_specification import NPCPayload
from app.knowledge.models import Concept
from app.generation.models import NPCPersona
from app.core.logging import get_logger

logger = get_logger("app.generation.npc_generator")


class NPCGenerator:
    """Generates thematic in-game NPC personas, dialogues, and lore snippets."""

    @staticmethod
    def generate_npc_payload(
        concept: Concept,
        persona: NPCPersona = NPCPersona.ARCHMAGE_ALAN,
        difficulty: int = 2,
    ) -> NPCPayload:
        """Constructs an NPCPayload matched to persona, concept, and difficulty level."""
        if persona == NPCPersona.ARCHMAGE_ALAN:
            npc_id = "archmage_alan"
            npc_name = "Grand Scribe Alan"
            dialogue = [
                f"Greetings, initiate. The ancient computing archives are flickering.",
                f"Today, we study {concept.name}. It is said that mastery over this principle allows one to wield order amidst computational chaos.",
                f"Examine the challenge carefully before casting your solution into the processor core.",
            ]
            lore = (
                f"Alan was among the first weavers of the Arcane Kernel, "
                f"binding raw electricity and silicon logic into eternal operational routines."
            )

        elif persona == NPCPersona.CHRONOS_WARDEN:
            npc_id = "chronos_warden"
            npc_name = "Chronos Warden of the Bus"
            dialogue = [
                f"Tick. Tock. Milliseconds slip like sand through an hourglass.",
                f"The system clock waits for no thread. With {concept.name}, every cycle counts.",
                f"Will your scheduling decisions prevent starvation, or doom the threads to wait in darkness?",
            ]
            lore = "The Warden maintains the synchronization pulses across the motherboard plains."

        elif persona == NPCPersona.GLITCH_SPRITE:
            npc_id = "glitch_sprite"
            npc_name = "Byte the Glitch Sprite"
            dialogue = [
                f"*Bzzzzt* Hey there! Did you know a single miscalculated burst can bottleneck everything?",
                f"Don't worry, I won't let the watchdog timer bite... unless you pick the wrong option on {concept.name}!",
                f"Take a hint if your registers start overheating!",
            ]
            lore = "A rogue packet given digital life by a stray cosmic ray hitting the cache."

        else:  # VOID_SENTINEL
            npc_id = "void_sentinel"
            npc_name = "Sentinel of the Deadlock Gate"
            dialogue = [
                f"Halt, mortal thread. None may traverse the Kernel Bridge without proving competence in {concept.name}.",
                f"Show me that you comprehend the flow of execution and the boundaries of preemption.",
            ]
            lore = "A vigilant daemon summoned to prevent infinite loops from collapsing reality."

        # Adapt dialogue if difficulty is high
        if difficulty >= 4:
            dialogue.append("Beware: This trial tests edge cases. Normal heuristics will fail you.")

        return NPCPayload(
            npc_id=npc_id,
            npc_name=npc_name,
            dialogue=dialogue,
            lore_snippet=lore,
        )


npc_generator = NPCGenerator()
