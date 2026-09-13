"""Game Specification Builder: Compiles validated learning content into Dasarth's Game Engine Contract."""

import logging
from typing import Dict, List, Optional
from schemas.knowledge import Concept
from schemas.learning_graph import LearningGraph
from schemas.game_spec import GameSpecification, Campaign, Chapter
from schemas.generation import GameMechanic, Mission, BossChallenge
from schemas.base import generate_id
from generation.mission_generator import MissionGenerator
from generation.boss_generator import BossGenerator
from validation.validator import ValidationEngine

logger = logging.getLogger("arcana.game_spec")


class GameSpecificationBuilder:
    """Assembles and validates complete Game Specifications for Dasarth's Game Engine."""

    def __init__(self, provider_router):
        self.router = provider_router
        self.mission_gen = MissionGenerator(provider_router)
        self.boss_gen = BossGenerator(provider_router)

    def build_specification(
        self,
        learning_graph: LearningGraph,
        concepts: List[Concept],
        campaign_title: str = "Arcana Learning Quest",
    ) -> GameSpecification:
        """Compile a full validated GameSpecification from a LearningGraph and Concept set."""
        concept_map: Dict[str, Concept] = {c.concept_id: c for c in concepts}
        valid_concept_ids = set(concept_map.keys())

        # Group concepts by tier into Chapters
        tier_map: Dict[int, List[Concept]] = {}
        for cid in learning_graph.topological_order:
            node = learning_graph.nodes.get(cid)
            c = concept_map.get(cid)
            if node and c:
                tier_map.setdefault(node.tier, []).append(c)

        # Fallback if no tiers
        if not tier_map:
            tier_map[1] = concepts

        chapters: List[Chapter] = []

        mechanics_cycle = [
            GameMechanic.QUIZ,
            GameMechanic.MATCHING,
            GameMechanic.ORDERING,
            GameMechanic.PUZZLE,
        ]

        for tier_num, tier_concepts in sorted(tier_map.items()):
            chapter_title = f"Chapter {tier_num}: {tier_concepts[0].name} & Foundations"
            missions: List[Mission] = []

            for idx, concept in enumerate(tier_concepts):
                mech = mechanics_cycle[idx % len(mechanics_cycle)]
                mission = self.mission_gen.generate_mission(concept=concept, mechanic=mech)
                missions.append(mission)

            # Build capstone boss challenge for the chapter
            boss: Optional[BossChallenge] = None
            if len(tier_concepts) >= 2:
                boss = self.boss_gen.generate_boss_challenge(
                    chapter_title=chapter_title,
                    cumulative_concepts=tier_concepts,
                )

            chapter = Chapter(
                id=generate_id("chp"),
                title=chapter_title,
                description=f"Mastery of {len(tier_concepts)} core concepts.",
                missions=missions,
                boss=boss,
            )
            chapters.append(chapter)

        campaign = Campaign(
            id=generate_id("cmp"),
            title=campaign_title,
            subject=learning_graph.subject,
            difficulty=2,
            chapters=chapters,
        )

        spec = GameSpecification(
            schema_version="1.0",
            campaign=campaign,
            metadata={
                "graph_id": learning_graph.graph_id,
                "total_concepts": len(concepts),
                "total_missions": sum(len(c.missions) for c in chapters),
            },
        )

        # MANDATORY: Multi-tier validation check before releasing specification
        report = ValidationEngine.validate_game_specification(spec, valid_concept_ids=valid_concept_ids)
        if not report.is_valid:
            error_msg = f"Generated GameSpecification failed validation: {'; '.join(report.errors)}"
            logger.critical(error_msg)
            raise RuntimeError(error_msg)

        logger.info(
            "GameSpecification successfully built & validated: %d chapters, %d missions",
            len(chapters),
            spec.metadata["total_missions"],
        )
        return spec
