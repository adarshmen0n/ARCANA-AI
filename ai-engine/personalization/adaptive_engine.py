"""Adaptive Learning Engine: Closed-loop personalization decision engine."""

import logging
from typing import Optional
from schemas.learning_graph import LearningGraph, LearningSequence
from schemas.personalization import StudentState, NextAction, ActionType
from learning_graph.planner import LearningPlanner

logger = logging.getLogger("arcana.personalization.adaptive")


class AdaptiveEngine:
    """Calculates optimal next educational action based on student state and learning graph."""

    @classmethod
    def determine_next_action(
        cls,
        graph: LearningGraph,
        state: StudentState,
    ) -> NextAction:
        plan: LearningSequence = LearningPlanner.create_plan(graph, student_state=state)

        # 1. Prioritize Revision if student has critical weak concepts
        if state.weak_concept_ids:
            weak_cid = state.weak_concept_ids[0]
            weak_node = graph.nodes.get(weak_cid)
            base_diff = weak_node.difficulty if weak_node else 2

            return NextAction(
                action_type=ActionType.REVISION,
                recommended_concept_id=weak_cid,
                target_difficulty=max(1, base_diff - 1),
                hint_intensity="high_scaffolding",
                explanation_level="simplified",
                rationale=(
                    f"Concept mastery is below threshold ({state.masteries[weak_cid].mastery_score:.2f}). "
                    "Triggering guided revision with progressive scaffolding."
                ),
            )

        # 2. Check if ready for a Boss capstone challenge
        # If all ready concepts in current chapter tier are mastered (> 0.75)
        mastered_count = sum(1 for m in state.masteries.values() if m.mastery_score >= 0.75)
        if mastered_count >= 3 and graph.terminal_concepts:
            # Check if all terminal dependencies met
            return NextAction(
                action_type=ActionType.BOSS,
                recommended_concept_id=graph.terminal_concepts[0],
                target_difficulty=4,
                hint_intensity="gentle",
                explanation_level="advanced",
                rationale="Learner demonstrates cumulative mastery across foundational concepts. Initiating Boss Challenge.",
            )

        # 3. Next normal learning milestone
        if plan.ordered_concept_ids:
            next_cid = plan.ordered_concept_ids[0]
            node = graph.nodes.get(next_cid)
            diff = node.difficulty if node else 2

            return NextAction(
                action_type=ActionType.LEARN,
                recommended_concept_id=next_cid,
                target_difficulty=diff,
                hint_intensity="standard",
                explanation_level="standard",
                rationale="Prerequisites cleared. Progressing to the next milestone in pedagogical sequence.",
            )

        # 4. Fallback if entire graph is complete
        fallback_cid = graph.topological_order[-1] if graph.topological_order else "unknown"
        return NextAction(
            action_type=ActionType.ADVANCE,
            recommended_concept_id=fallback_cid,
            target_difficulty=5,
            hint_intensity="gentle",
            explanation_level="advanced",
            rationale="Campaign objectives achieved. Unlocking advanced mastery challenges.",
        )
