"""Learning Planner: Computes personalized pedagogical progression through the Learning Graph."""

import logging
from typing import List, Optional
from schemas.learning_graph import LearningGraph, LearningSequence
from schemas.personalization import StudentState
from schemas.base import generate_id

logger = logging.getLogger("arcana.planner")


class LearningPlanner:
    """Plans ordered learning pathways respecting prerequisites and student mastery."""

    @classmethod
    def create_plan(
        cls,
        graph: LearningGraph,
        student_state: Optional[StudentState] = None,
    ) -> LearningSequence:
        """Compute the recommended learning sequence, revision needs, and deferred milestones."""
        ordered: List[str] = []
        revision: List[str] = []
        deferred: List[str] = []
        advanced: List[str] = []

        # Completed or mastered concepts set
        mastered_cids = set()
        if student_state:
            for cid, mastery in student_state.masteries.items():
                if mastery.mastery_score >= 0.7:
                    mastered_cids.add(cid)
                elif mastery.mastery_score < 0.5 and mastery.attempts > 0:
                    revision.append(cid)

        # Evaluate every concept according to topological order
        for cid in graph.topological_order:
            node = graph.nodes.get(cid)
            if not node:
                continue

            # Check if all prerequisites are fulfilled
            prereqs_met = all(pid in mastered_cids for pid in node.prerequisite_ids)

            if cid in mastered_cids:
                # Already mastered; mark as advanced milestone if expert level
                if node.difficulty >= 4:
                    advanced.append(cid)
                continue

            if prereqs_met:
                ordered.append(cid)
            else:
                deferred.append(cid)

        # Fallback: if no student state or no concepts cleared, start from root concepts
        if not ordered and graph.root_concepts:
            ordered = [cid for cid in graph.topological_order if cid not in mastered_cids]

        return LearningSequence(
            sequence_id=generate_id("seq"),
            ordered_concept_ids=ordered,
            revision_concept_ids=revision,
            advanced_concept_ids=advanced,
            deferred_concept_ids=deferred,
        )
