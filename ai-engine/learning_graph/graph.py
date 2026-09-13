"""Learning Graph Engine: DAG Construction, Cycle Detection, and Topological Sorting."""

from collections import defaultdict, deque
import logging
from typing import Dict, List, Set, Tuple
from schemas.knowledge import Concept, Relationship, RelationshipType, KnowledgeGraph
from schemas.learning_graph import LearningGraph, LearningGraphNode, LearningGraphEdge
from schemas.base import generate_id

logger = logging.getLogger("arcana.learning_graph")


class LearningGraphEngine:
    """Builds and validates Directed Acyclic Reasoning Graphs for ARCANA."""

    @classmethod
    def build_from_knowledge_graph(cls, kg: KnowledgeGraph) -> LearningGraph:
        """Construct a validated, topologically ordered LearningGraph from a KnowledgeGraph."""
        nodes: Dict[str, LearningGraphNode] = {}
        edges: List[LearningGraphEdge] = []

        # 1. Initialize nodes
        for c in kg.concepts:
            nodes[c.concept_id] = LearningGraphNode(
                concept_id=c.concept_id,
                name=c.name,
                difficulty=c.difficulty,
                importance=c.importance,
                prerequisite_ids=[],
                dependent_ids=[],
                depth=0,
                tier=1,
            )

        # 2. Build adjacency for prerequisite / dependency edges
        prereq_edges: List[Tuple[str, str, float]] = []
        for rel in kg.relationships:
            if rel.relationship == RelationshipType.PREREQUISITE_OF:
                src, tgt = rel.from_concept_id, rel.to_concept_id
                if src in nodes and tgt in nodes:
                    prereq_edges.append((src, tgt, rel.confidence))
            elif rel.relationship == RelationshipType.DEPENDS_ON:
                src, tgt = rel.to_concept_id, rel.from_concept_id
                if src in nodes and tgt in nodes:
                    prereq_edges.append((src, tgt, rel.confidence))

        # 3. Cycle detection and topological ordering (Kahn's Algorithm)
        in_degree: Dict[str, int] = {cid: 0 for cid in nodes}
        adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)

        for src, tgt, conf in prereq_edges:
            adj[src].append((tgt, conf))
            in_degree[tgt] += 1

        queue = deque([cid for cid, deg in in_degree.items() if deg == 0])
        topological_order: List[str] = []

        while queue:
            curr = queue.popleft()
            topological_order.append(curr)

            for neighbor, _ in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Cycle resolution: If not all nodes were visited, an invalid cycle existed
        is_acyclic = len(topological_order) == len(nodes)
        if not is_acyclic:
            logger.warning(
                "Cycle detected in prerequisite graph. Resolving by falling back to difficulty ordering."
            )
            # Fallback sort by concept difficulty and importance
            remaining = [cid for cid in nodes if cid not in topological_order]
            remaining.sort(key=lambda cid: (nodes[cid].difficulty, nodes[cid].importance))
            topological_order.extend(remaining)

        # 4. Finalize node dependencies, depth, and edge models
        valid_edge_set: Set[Tuple[str, str]] = set()
        for src, tgt, conf in prereq_edges:
            # Only keep edges that flow forward in the topological order
            if topological_order.index(src) < topological_order.index(tgt):
                if tgt not in nodes[src].dependent_ids:
                    nodes[src].dependent_ids.append(tgt)
                if src not in nodes[tgt].prerequisite_ids:
                    nodes[tgt].prerequisite_ids.append(src)
                if (src, tgt) not in valid_edge_set:
                    valid_edge_set.add((src, tgt))
                    edges.append(
                        LearningGraphEdge(
                            source_id=src,
                            target_id=tgt,
                            relationship_type=RelationshipType.PREREQUISITE_OF,
                            confidence=conf,
                        )
                    )

        # 5. Compute topological depth and tiers
        for cid in topological_order:
            node = nodes[cid]
            if not node.prerequisite_ids:
                node.depth = 0
            else:
                max_parent_depth = max(nodes[pid].depth for pid in node.prerequisite_ids)
                node.depth = max_parent_depth + 1
            node.tier = (node.depth // 2) + 1

        root_concepts = [cid for cid, n in nodes.items() if not n.prerequisite_ids]
        terminal_concepts = [cid for cid, n in nodes.items() if not n.dependent_ids]

        return LearningGraph(
            graph_id=generate_id("lg"),
            subject=kg.subject,
            nodes=nodes,
            edges=edges,
            root_concepts=root_concepts,
            terminal_concepts=terminal_concepts,
            topological_order=topological_order,
            is_acyclic=is_acyclic,
        )
