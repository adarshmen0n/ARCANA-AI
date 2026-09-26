"""Learning Graph Service managing path generation and adaptive next-concept selection."""

from typing import Dict, List, Optional, Set, Tuple
from app.core.errors import ResourceNotFoundException
from app.core.logging import get_logger
from app.knowledge.engine import knowledge_engine
from app.learning_graph.builder import LearningGraphBuilder
from app.learning_graph.dag import DirectedAcyclicGraph
from app.learning_graph.models import LearningNode, LearningPath, NextConceptRecommendation

logger = get_logger("app.learning_graph.service")


class LearningGraphService:
    """Coordinates learning graph building, path planning, and next-concept adaptive recommendation."""

    def __init__(self):
        self._graphs_by_doc: Dict[str, DirectedAcyclicGraph] = {}
        self._paths_by_doc: Dict[str, LearningPath] = {}

    def get_or_build_graph(self, document_id: str) -> Tuple[DirectedAcyclicGraph, LearningPath]:
        """Returns existing graph or constructs one from knowledge extraction."""
        if document_id not in self._graphs_by_doc:
            concepts = knowledge_engine.get_concepts(document_id)
            relationships = knowledge_engine.get_relationships(document_id)

            if not concepts:
                raise ResourceNotFoundException("Concepts for Document", document_id)

            dag, path = LearningGraphBuilder.build_graph(document_id, concepts, relationships)
            self._graphs_by_doc[document_id] = dag
            self._paths_by_doc[document_id] = path
            logger.info(f"Built Learning Graph for {document_id}: {path.total_nodes} nodes.")

        return self._graphs_by_doc[document_id], self._paths_by_doc[document_id]

    def get_learning_path(self, document_id: str) -> LearningPath:
        """Retrieves the full topological learning path for a document."""
        _, path = self.get_or_build_graph(document_id)
        return path

    def recommend_next_concept(
        self,
        document_id: str,
        completed_concept_ids: List[str],
        weak_concept_id: Optional[str] = None,
    ) -> NextConceptRecommendation:
        """Selects the optimal next concept to learn or remediate."""
        dag, path = self.get_or_build_graph(document_id)
        completed_set: Set[str] = set(completed_concept_ids)
        node_map = {n.concept_id: n for n in path.nodes}

        # Case 1: Remediation requested for a struggling concept
        if weak_concept_id and weak_concept_id in node_map:
            ancestors = dag.get_all_ancestors(weak_concept_id)
            uncompleted_prereqs = [a for a in ancestors if a not in completed_set]

            if uncompleted_prereqs:
                # Pick the earliest uncompleted prerequisite
                remedial_id = uncompleted_prereqs[0]
                target_node = node_map[remedial_id]
                return NextConceptRecommendation(
                    recommended_concept=target_node,
                    reason=(
                        f"Student is struggling with '{node_map[weak_concept_id].name}'. "
                        f"Remediation requires reviewing essential prerequisite: '{target_node.name}'."
                    ),
                    prerequisites_satisfied=True,
                    is_remediation=True,
                    alternative_ready_concepts=dag.get_ready_nodes(completed_set),
                )
            else:
                # Review the weak concept directly with lower difficulty
                target_node = node_map[weak_concept_id]
                return NextConceptRecommendation(
                    recommended_concept=target_node,
                    reason=f"Reinforcing concept '{target_node.name}' through targeted practice.",
                    prerequisites_satisfied=True,
                    is_remediation=True,
                    alternative_ready_concepts=dag.get_ready_nodes(completed_set),
                )

        # Case 2: Standard progression - select next ready node
        ready_ids = dag.get_ready_nodes(completed_set)

        if not ready_ids:
            # All concepts completed
            last_node = path.nodes[-1]
            return NextConceptRecommendation(
                recommended_concept=last_node,
                reason="All concepts in this learning path have been completed! Recommending mastery review.",
                prerequisites_satisfied=True,
                is_remediation=False,
                alternative_ready_concepts=[],
            )

        # Choose the first ready concept in topological order
        chosen_id = ready_ids[0]
        chosen_node = node_map[chosen_id]

        return NextConceptRecommendation(
            recommended_concept=chosen_node,
            reason=f"Prerequisites completed. Ready to advance to '{chosen_node.name}'.",
            prerequisites_satisfied=True,
            is_remediation=False,
            alternative_ready_concepts=ready_ids[1:],
        )


# Global singleton instance
learning_graph_service = LearningGraphService()
