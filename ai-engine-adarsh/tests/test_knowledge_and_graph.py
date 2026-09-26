"""Unit and integration tests for Knowledge Engine and Learning Graph Builder."""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure ai-engine-adarsh is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.learning_graph.dag import DirectedAcyclicGraph
from app.knowledge.models import Concept, ConceptRelationship, RelationshipType
from app.learning_graph.builder import LearningGraphBuilder
from app.learning_graph.service import learning_graph_service

client = TestClient(app)


def test_dag_topological_sort_and_cycle_prevention():
    """Verify DAG handles edge addition, prevents cycles, and sorts topologically."""
    dag = DirectedAcyclicGraph()

    # Add linear dependency: A -> B -> C
    assert dag.add_edge("A", "B") is True
    assert dag.add_edge("B", "C") is True

    # Attempt to introduce a cycle: C -> A
    assert dag.add_edge("C", "A") is False

    # Topological order must strictly be ['A', 'B', 'C']
    order = dag.topological_sort()
    assert order == ["A", "B", "C"]

    # Prerequisites & dependents
    assert dag.get_prerequisites("B") == ["A"]
    assert dag.get_dependents("B") == ["C"]
    assert dag.get_all_ancestors("C") == {"A", "B"}


def test_dag_ready_nodes():
    """Verify ready nodes calculation based on student mastery set."""
    dag = DirectedAcyclicGraph()
    dag.add_edge("Foundations", "Intermediate")
    dag.add_edge("Intermediate", "Advanced")

    # When student has completed nothing, only "Foundations" is ready
    assert dag.get_ready_nodes(set()) == ["Foundations"]

    # When student completed Foundations, "Intermediate" is ready
    assert dag.get_ready_nodes({"Foundations"}) == ["Intermediate"]

    # When student completed Intermediate, "Advanced" is ready
    assert dag.get_ready_nodes({"Foundations", "Intermediate"}) == ["Advanced"]


def test_learning_graph_builder():
    """Verify LearningGraphBuilder creates valid LearningPath from concepts."""
    concepts = [
        Concept(
            concept_id="process_concept",
            name="Process Concept",
            topic="CPU Scheduling",
            definition="A process is a program in execution.",
            difficulty=1,
        ),
        Concept(
            concept_id="fcfs_scheduling",
            name="FCFS Scheduling",
            topic="CPU Scheduling",
            definition="Processes run in order of arrival.",
            difficulty=2,
        ),
        Concept(
            concept_id="sjf_scheduling",
            name="SJF Scheduling",
            topic="CPU Scheduling",
            definition="Shortest burst jobs run first.",
            difficulty=3,
        ),
    ]

    relationships = [
        ConceptRelationship(
            source_concept_id="process_concept",
            relationship_type=RelationshipType.PREREQUISITE_OF,
            target_concept_id="fcfs_scheduling",
        ),
        ConceptRelationship(
            source_concept_id="fcfs_scheduling",
            relationship_type=RelationshipType.PREREQUISITE_OF,
            target_concept_id="sjf_scheduling",
        ),
    ]

    dag, path = LearningGraphBuilder.build_graph("doc-os-test", concepts, relationships)

    assert path.total_nodes == 3
    assert path.ordered_concept_ids == ["process_concept", "fcfs_scheduling", "sjf_scheduling"]
    assert path.nodes[1].prerequisites == ["process_concept"]
    assert path.nodes[1].dependents == ["sjf_scheduling"]


def test_api_knowledge_and_graph_workflow():
    """Verify HTTP flow: Upload document -> Extract knowledge -> Get graph -> Recommend next concept."""
    doc_text = (
        b"Chapter 5: CPU Scheduling\n\n"
        b"5.1 Process States\n"
        b"A process changes state as it executes: new, ready, running, waiting, terminated.\n\n"
        b"5.2 CPU Scheduler\n"
        b"Whenever the CPU becomes idle, the OS selects a process from the ready queue.\n\n"
        b"5.3 FCFS Scheduling\n"
        b"First-Come, First-Served scheduling allocates CPU to the process that requests it first."
    )

    # 1. Upload
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("os_full.txt", doc_text, "text/plain")},
    )
    doc_id = upload_res.json()["document_id"]

    # 2. Extract Knowledge
    know_res = client.post(f"/api/v1/documents/{doc_id}/knowledge")
    assert know_res.status_code == 200
    know_data = know_res.json()
    assert know_data["total_concepts"] >= 2
    assert know_data["total_relationships"] >= 1

    # 3. Retrieve Learning Graph
    graph_res = client.get(f"/api/v1/documents/{doc_id}/graph")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert len(graph_data["ordered_concept_ids"]) >= 2

    first_concept_id = graph_data["ordered_concept_ids"][0]

    # 4. Recommend Next Concept (Fresh student, 0 completed)
    next_res = client.post(
        f"/api/v1/documents/{doc_id}/next-concept",
        json={"completed_concept_ids": []},
    )
    assert next_res.status_code == 200
    next_data = next_res.json()
    assert next_data["recommended_concept"]["concept_id"] == first_concept_id
    assert next_data["is_remediation"] is False

    # 5. Recommend Next Concept (First concept completed)
    second_res = client.post(
        f"/api/v1/documents/{doc_id}/next-concept",
        json={"completed_concept_ids": [first_concept_id]},
    )
    assert second_res.status_code == 200
    second_data = second_res.json()
    assert second_data["recommended_concept"]["concept_id"] != first_concept_id
