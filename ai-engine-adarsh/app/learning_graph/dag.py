"""Pure-Python Directed Acyclic Graph (DAG) for deterministic curriculum traversal."""

from collections import deque
from typing import Dict, List, Optional, Set


class DirectedAcyclicGraph:
    """Deterministic Directed Acyclic Graph supporting topological sorting and prerequisite traversal."""

    def __init__(self):
        # node_id -> dict of attributes
        self._nodes: Dict[str, dict] = {}
        # node_id -> set of successor/dependent node_ids (outgoing edges: prereq -> dependent)
        self._adjacency: Dict[str, Set[str]] = {}
        # node_id -> set of predecessor/prerequisite node_ids (incoming edges: prereq -> dependent)
        self._predecessors: Dict[str, Set[str]] = {}

    def add_node(self, node_id: str, attributes: Optional[dict] = None) -> None:
        """Adds a concept node to the graph."""
        if node_id not in self._nodes:
            self._nodes[node_id] = attributes or {}
            self._adjacency[node_id] = set()
            self._predecessors[node_id] = set()

    def has_path(self, start: str, target: str) -> bool:
        """Checks if a directed path exists from start to target using BFS."""
        if start == target:
            return True
        visited = set()
        queue = deque([start])

        while queue:
            curr = queue.popleft()
            if curr == target:
                return True
            for neighbor in self._adjacency.get(curr, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    def add_edge(self, source_id: str, target_id: str) -> bool:
        """Adds a directed edge from source to target (source is prerequisite for target).

        Guarantees acyclicity: if adding the edge would introduce a cycle, the edge is rejected.
        Returns True if edge was added, False if rejected due to cycle.
        """
        self.add_node(source_id)
        self.add_node(target_id)

        # Cycle check: If target can already reach source, adding source -> target creates a cycle
        if self.has_path(target_id, source_id):
            return False

        self._adjacency[source_id].add(target_id)
        self._predecessors[target_id].add(source_id)
        return True

    def get_prerequisites(self, node_id: str) -> List[str]:
        """Returns direct prerequisite concept IDs for this node."""
        return sorted(list(self._predecessors.get(node_id, set())))

    def get_dependents(self, node_id: str) -> List[str]:
        """Returns direct dependent concept IDs that unlock after this node."""
        return sorted(list(self._adjacency.get(node_id, set())))

    def get_all_ancestors(self, node_id: str) -> Set[str]:
        """Recursively retrieves all prerequisite ancestors (transitive closure) for remediation."""
        ancestors: Set[str] = set()
        queue = deque(self.get_prerequisites(node_id))

        while queue:
            curr = queue.popleft()
            if curr not in ancestors:
                ancestors.add(curr)
                queue.extend(self.get_prerequisites(curr))

        return ancestors

    def topological_sort(self) -> List[str]:
        """Returns a canonical topological ordering of all concepts using Kahn's algorithm."""
        in_degree = {n: len(self._predecessors[n]) for n in self._nodes}
        queue = deque([n for n, deg in in_degree.items() if deg == 0])
        ordered: List[str] = []

        while queue:
            curr = queue.popleft()
            ordered.append(curr)

            for neighbor in sorted(list(self._adjacency[curr])):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If any disconnected or unreached nodes remain, append them safely
        if len(ordered) < len(self._nodes):
            for n in self._nodes:
                if n not in ordered:
                    ordered.append(n)

        return ordered

    def get_ready_nodes(self, completed_ids: Set[str]) -> List[str]:
        """Finds all concepts that have NOT been completed, but whose prerequisites are all satisfied."""
        ready: List[str] = []

        for node_id in self.topological_sort():
            if node_id in completed_ids:
                continue

            prereqs = self._predecessors.get(node_id, set())
            if prereqs.issubset(completed_ids):
                ready.append(node_id)

        return ready

    def get_node_data(self, node_id: str) -> dict:
        return self._nodes.get(node_id, {})

    @property
    def nodes(self) -> List[str]:
        return list(self._nodes.keys())
