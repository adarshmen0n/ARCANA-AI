"""Unit tests for ValidationEngine and GameSpecificationBuilder."""

import json
import pytest
from schemas.knowledge import Concept, Relationship, RelationshipType, KnowledgeGraph
from schemas.generation import GameMechanic
from learning_graph.graph import LearningGraphEngine
from validation.validator import ValidationEngine
from game_specification.builder import GameSpecificationBuilder
from providers.mock import MockLLMProvider
from providers.router import ProviderRouter


@pytest.fixture
def sample_kg():
    c1 = Concept(concept_id="c_cpu", name="CPU Scheduling", description="Allocates CPU time.", difficulty=2)
    c2 = Concept(concept_id="c_rr", name="Round Robin", description="Time slice scheduling.", difficulty=3, prerequisite_ids=["c_cpu"])
    r1 = Relationship(from_concept_id="c_cpu", to_concept_id="c_rr", relationship=RelationshipType.PREREQUISITE_OF)

    return KnowledgeGraph(subject="OS", document_id="doc_os", concepts=[c1, c2], relationships=[r1])


def test_game_spec_builder_and_validation(sample_kg):
    router = ProviderRouter(primary_provider=MockLLMProvider())
    lg = LearningGraphEngine.build_from_knowledge_graph(sample_kg)
    builder = GameSpecificationBuilder(router)

    spec = builder.build_specification(lg, sample_kg.concepts, campaign_title="Operating Systems Odyssey")

    assert spec.schema_version == "1.0"
    assert spec.campaign.subject == "OS"
    assert len(spec.campaign.chapters) >= 1

    # Verify JSON serializability for Dasarth's Game Engine
    spec_json = spec.model_dump_json()
    parsed = json.loads(spec_json)
    assert parsed["schema_version"] == "1.0"
    assert "campaign" in parsed


def test_validation_rejects_code_injection(sample_kg):
    router = ProviderRouter(primary_provider=MockLLMProvider())
    lg = LearningGraphEngine.build_from_knowledge_graph(sample_kg)
    builder = GameSpecificationBuilder(router)

    spec = builder.build_specification(lg, sample_kg.concepts)

    # Malicious injection test
    spec.campaign.chapters[0].missions[0].title = "Malicious Mission eval(import os)"

    report = ValidationEngine.validate_game_specification(spec)
    assert report.is_valid is False
    assert any("Prohibited executable code pattern" in err for err in report.errors)


def test_validation_rejects_invalid_schema_version(sample_kg):
    router = ProviderRouter(primary_provider=MockLLMProvider())
    lg = LearningGraphEngine.build_from_knowledge_graph(sample_kg)
    builder = GameSpecificationBuilder(router)

    spec = builder.build_specification(lg, sample_kg.concepts)
    spec.schema_version = "0.9-alpha"

    report = ValidationEngine.validate_game_specification(spec)
    assert report.is_valid is False
    assert any("Invalid schema_version" in err for err in report.errors)
