"""Unit tests for Personalization, Mastery, Adaptive Engine, and AI Tutor."""

import pytest
from schemas.personalization import StudentState, ConceptMastery, GameplayEvent, ActionType
from schemas.learning_graph import LearningGraph, LearningGraphNode
from schemas.document import Chunk
from personalization.mastery_engine import MasteryEngine
from personalization.adaptive_engine import AdaptiveEngine
from services.tutor import AITutorService
from embeddings.engine import EmbeddingEngine
from retrieval.vector_store import VectorStore
from rag.engine import RAGEngine
from providers.mock import MockEmbeddingProvider, MockLLMProvider
from providers.router import ProviderRouter


def test_mastery_engine_event_processing():
    state = StudentState(student_id="student_1")
    event1 = GameplayEvent(
        student_id="student_1",
        mission_id="m1",
        concept_id="c_var",
        is_correct=True,
        hints_used=0,
        response_time_seconds=6.0,
    )

    updated = MasteryEngine.process_gameplay_event(state, event1)
    assert "c_var" in updated.masteries
    assert updated.masteries["c_var"].mastery_score >= 0.9  # bonus for speed and zero hints
    assert updated.total_xp == 20
    assert updated.total_coins == 5
    assert updated.current_level == 1

    # Failed attempt with many hints reduces mastery and triggers weak concept list
    event2 = GameplayEvent(
        student_id="student_1",
        mission_id="m2",
        concept_id="c_loop",
        is_correct=False,
        hints_used=3,
        response_time_seconds=30.0,
    )
    updated2 = MasteryEngine.process_gameplay_event(updated, event2)
    assert updated2.masteries["c_loop"].mastery_score <= 0.2
    assert "c_loop" in updated2.weak_concept_ids


def test_adaptive_engine_triggers_revision():
    nodes = {
        "c1": LearningGraphNode(concept_id="c1", name="Variables", difficulty=1),
        "c2": LearningGraphNode(concept_id="c2", name="Loops", difficulty=2, prerequisite_ids=["c1"]),
    }
    graph = LearningGraph(nodes=nodes, topological_order=["c1", "c2"])

    # State with c1 weak
    state = StudentState(
        student_id="stu_rev",
        weak_concept_ids=["c1"],
        masteries={"c1": ConceptMastery(concept_id="c1", mastery_score=0.4, attempts=2)},
    )

    action = AdaptiveEngine.determine_next_action(graph, state)
    assert action.action_type == ActionType.REVISION
    assert action.recommended_concept_id == "c1"
    assert action.hint_intensity == "high_scaffolding"


def test_ai_tutor_service():
    embed = EmbeddingEngine(MockEmbeddingProvider(dimension=32))
    vstore = VectorStore()
    chunk = Chunk(chunk_id="chk_math", document_id="d1", chapter="Math", section="Algebra", text="Variables hold numbers.")
    vstore.add_chunks([chunk], [embed.embed_text(chunk.text)])

    router = ProviderRouter(
        primary_provider=MockLLMProvider(),
        embedding_provider=MockEmbeddingProvider(dimension=32),
    )
    rag = RAGEngine(vector_store=vstore, embedding_engine=embed, provider_router=router)
    tutor = AITutorService(rag_engine=rag, provider_router=router)

    student_state = StudentState(student_id="s1", current_level=2)
    resp = tutor.ask_tutor("What is a variable?", student_state=student_state)

    assert resp.adapted_for_level == 2
    assert "chk_math" in resp.source_references
    assert "MockLLM response" in resp.answer
