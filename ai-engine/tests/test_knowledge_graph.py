"""Unit tests for Knowledge Engine, Learning Graph, Planner, and Difficulty Engine."""

import pytest
from schemas.document import Chunk
from schemas.knowledge import Concept, Relationship, RelationshipType, KnowledgeGraph
from schemas.personalization import StudentState, ConceptMastery
from knowledge.extractor import KnowledgeEngine
from learning_graph.graph import LearningGraphEngine
from learning_graph.planner import LearningPlanner
from difficulty.engine import DifficultyEngine
from providers.mock import MockLLMProvider
from providers.router import ProviderRouter


def test_knowledge_extraction_and_relationships():
    router = ProviderRouter(primary_provider=MockLLMProvider())
    ke = KnowledgeEngine(provider_router=router)

    chunks = [
        Chunk(chunk_id="c1", document_id="doc1", chapter="Python", section="Variables", text="Variables store values in memory."),
        Chunk(chunk_id="c2", document_id="doc1", chapter="Python", section="Loops", text="Loops repeat execution of statements."),
        Chunk(chunk_id="c3", document_id="doc1", chapter="Python", section="Recursion", text="Recursion is an algorithm where functions call themselves."),
    ]

    kg = ke.build_knowledge_graph(chunks, document_id="doc1", subject="Python")
    assert len(kg.concepts) == 3
    assert any(c.name == "Variables" for c in kg.concepts)
    assert any(c.name == "Recursion" for c in kg.concepts)
    # Recursion has higher difficulty due to algorithmic keyword
    rec_c = next(c for c in kg.concepts if c.name == "Recursion")
    assert rec_c.difficulty >= 3
    assert len(kg.relationships) >= 2


def test_learning_graph_topological_dag():
    c1 = Concept(concept_id="c_var", name="Variables", description="Stores values", difficulty=1)
    c2 = Concept(concept_id="c_cond", name="Conditionals", description="Branching logic", difficulty=2, prerequisite_ids=["c_var"])
    c3 = Concept(concept_id="c_loop", name="Loops", description="Repeated blocks", difficulty=2, prerequisite_ids=["c_cond"])

    r1 = Relationship(from_concept_id="c_var", to_concept_id="c_cond", relationship=RelationshipType.PREREQUISITE_OF)
    r2 = Relationship(from_concept_id="c_cond", to_concept_id="c_loop", relationship=RelationshipType.PREREQUISITE_OF)

    kg = KnowledgeGraph(subject="Programming", document_id="d1", concepts=[c1, c2, c3], relationships=[r1, r2])
    lg = LearningGraphEngine.build_from_knowledge_graph(kg)

    assert lg.is_acyclic is True
    assert lg.topological_order == ["c_var", "c_cond", "c_loop"]
    assert lg.nodes["c_var"].depth == 0
    assert lg.nodes["c_cond"].depth == 1
    assert lg.nodes["c_loop"].depth == 2
    assert "c_var" in lg.root_concepts
    assert "c_loop" in lg.terminal_concepts


def test_difficulty_engine_content_and_learner():
    from schemas.learning_graph import LearningGraphNode

    node = LearningGraphNode(
        concept_id="c_os",
        name="Deadlock Resolution",
        difficulty=3,
        importance=0.9,
        prerequisite_ids=["p1", "p2", "p3"],
        depth=3,
    )
    content_diff = DifficultyEngine.calculate_content_difficulty(node)
    assert content_diff >= 4  # Elevated due to depth >= 3 and 3 prerequisites

    # High mastery student -> reduced difficulty
    expert_student = ConceptMastery(concept_id="c_os", mastery_score=0.95, attempts=2, hints_used=0)
    assert DifficultyEngine.calculate_learner_difficulty(content_diff, expert_student) == content_diff - 1

    # Struggling student -> elevated difficulty
    struggling_student = ConceptMastery(concept_id="c_os", mastery_score=0.3, attempts=3, hints_used=7)
    assert DifficultyEngine.calculate_learner_difficulty(content_diff, struggling_student) == min(5, content_diff + 1)


def test_learning_planner_prerequisites_and_revision():
    c1 = Concept(concept_id="c_var", name="Variables", description="Variables", difficulty=1)
    c2 = Concept(concept_id="c_cond", name="Conditionals", description="Conditionals", difficulty=2, prerequisite_ids=["c_var"])
    c3 = Concept(concept_id="c_loop", name="Loops", description="Loops", difficulty=2, prerequisite_ids=["c_cond"])

    r1 = Relationship(from_concept_id="c_var", to_concept_id="c_cond", relationship=RelationshipType.PREREQUISITE_OF)
    r2 = Relationship(from_concept_id="c_cond", to_concept_id="c_loop", relationship=RelationshipType.PREREQUISITE_OF)

    kg = KnowledgeGraph(subject="Programming", document_id="d1", concepts=[c1, c2, c3], relationships=[r1, r2])
    lg = LearningGraphEngine.build_from_knowledge_graph(kg)

    # Student has mastered Variables (0.9), but struggled on Conditionals (0.4)
    state = StudentState(
        student_id="stu_01",
        masteries={
            "c_var": ConceptMastery(concept_id="c_var", mastery_score=0.9, attempts=2),
            "c_cond": ConceptMastery(concept_id="c_cond", mastery_score=0.4, attempts=3, hints_used=5),
        },
    )

    plan = LearningPlanner.create_plan(lg, student_state=state)

    # Conditionals should trigger revision
    assert "c_cond" in plan.revision_concept_ids
    # Loops requires Conditionals to be mastered (score >= 0.7), so loops should be deferred
    assert "c_loop" in plan.deferred_concept_ids
