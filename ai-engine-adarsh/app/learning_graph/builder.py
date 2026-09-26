"""Learning Graph Builder constructing DAGs from concepts and relationships."""

import uuid
from typing import List, Tuple
from app.core.logging import get_logger
from app.knowledge.models import Concept, ConceptRelationship, RelationshipType
from app.learning_graph.dag import DirectedAcyclicGraph
from app.learning_graph.models import LearningNode, LearningPath

logger = get_logger("app.learning_graph.builder")


class LearningGraphBuilder:
    """Builds and validates Directed Acyclic Learning Graphs from extracted knowledge."""

    @staticmethod
    def build_graph(
        document_id: str,
        concepts: List[Concept],
        relationships: List[ConceptRelationship],
    ) -> Tuple[DirectedAcyclicGraph, LearningPath]:
        """Constructs a deterministic DAG and extracts the canonical topological LearningPath."""
        dag = DirectedAcyclicGraph()
        concept_map = {c.concept_id: c for c in concepts}

        # 1. Add all concept nodes
        for c in concepts:
            dag.add_node(
                c.concept_id,
                attributes={
                    "name": c.name,
                    "difficulty": c.difficulty,
                    "topic": c.topic,
                    "definition": c.definition,
                },
            )

        # 2. Add edges adhering to prerequisite semantics
        for rel in relationships:
            src = rel.source_concept_id
            tgt = rel.target_concept_id

            if src not in concept_map or tgt not in concept_map:
                continue

            if rel.relationship_type in (
                RelationshipType.PREREQUISITE_OF,
                RelationshipType.FOLLOWS,
                RelationshipType.REQUIRES,
            ):
                added = dag.add_edge(src, tgt)
                if not added:
                    logger.warning(f"Cycle detected! Rejected edge: {src} -> {tgt}")
            elif rel.relationship_type == RelationshipType.DEPENDS_ON:
                # tgt is prerequisite for src
                added = dag.add_edge(tgt, src)
                if not added:
                    logger.warning(f"Cycle detected! Rejected dependency edge: {tgt} -> {src}")

        # 3. Compute topological order
        ordered_ids = dag.topological_sort()

        # 4. Construct LearningNodes with direct prerequisites and dependents
        learning_nodes: List[LearningNode] = []
        for cid in ordered_ids:
            c = concept_map[cid]
            learning_nodes.append(
                LearningNode(
                    concept_id=cid,
                    name=c.name,
                    difficulty=c.difficulty,
                    topic=c.topic,
                    prerequisites=dag.get_prerequisites(cid),
                    dependents=dag.get_dependents(cid),
                )
            )

        path_id = f"path-{document_id.replace('-', '')[:8]}-{uuid.uuid4().hex[:6]}"
        learning_path = LearningPath(
            path_id=path_id,
            document_id=document_id,
            ordered_concept_ids=ordered_ids,
            total_nodes=len(learning_nodes),
            nodes=learning_nodes,
        )

        return dag, learning_path
