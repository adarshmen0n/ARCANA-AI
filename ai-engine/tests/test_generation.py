"""Unit tests for the independent Generation Engine components."""

import pytest
from schemas.knowledge import Concept
from schemas.generation import GameMechanic, QuestionType
from generation import (
    ObjectiveGenerator,
    LessonGenerator,
    QuestionGenerator,
    HintGenerator,
    StoryGenerator,
    NPCGenerator,
    MissionGenerator,
    BossGenerator,
)
from providers.mock import MockLLMProvider
from providers.router import ProviderRouter


@pytest.fixture
def router():
    return ProviderRouter(primary_provider=MockLLMProvider())


@pytest.fixture
def sample_concept():
    return Concept(
        concept_id="c_func",
        name="Functions",
        description="Functions organize reusable blocks of code.",
        importance=0.9,
        difficulty=2,
        source_chunk_ids=["chk_01"],
    )


def test_objective_generator(router, sample_concept):
    gen = ObjectiveGenerator(router)
    obj = gen.generate_objective(sample_concept)
    assert obj.concept_id == sample_concept.concept_id
    assert obj.bloom_level == "understand"
    assert len(obj.success_criteria) == 3


def test_lesson_generator(router, sample_concept):
    obj_gen = ObjectiveGenerator(router)
    obj = obj_gen.generate_objective(sample_concept)
    lesson_gen = LessonGenerator(router)
    lesson = lesson_gen.generate_lesson(sample_concept, obj)

    assert "Functions" in lesson.title
    assert len(lesson.examples) >= 2
    assert len(lesson.key_points) >= 3
    assert lesson.analogy is not None
    assert lesson.source_references == ["chk_01"]


def test_question_generator_mcq_answer_key(router, sample_concept):
    gen = QuestionGenerator(router)
    questions = gen.generate_questions_for_concept(sample_concept, count=2)
    assert len(questions) == 2

    # Verify MCQ answer key integrity
    mcq = questions[0]
    assert mcq.type == QuestionType.MCQ
    assert mcq.correct_answer in mcq.options
    assert len(mcq.options) == 4
    assert mcq.explanation != ""


def test_hint_generator_tiers(router, sample_concept):
    q_gen = QuestionGenerator(router)
    q = q_gen.generate_questions_for_concept(sample_concept, count=1)[0]

    h_gen = HintGenerator(router)
    hints = h_gen.generate_progressive_hints(q)
    assert len(hints) == 4
    assert [h.tier for h in hints] == [1, 2, 3, 4]


def test_mission_generator_synthesis(router, sample_concept):
    m_gen = MissionGenerator(router)
    mission = m_gen.generate_mission(sample_concept, mechanic=GameMechanic.MATCHING)

    assert mission.mechanic == GameMechanic.MATCHING
    assert mission.concept_ids == [sample_concept.concept_id]
    assert len(mission.questions) == 2
    assert len(mission.hints) == 8  # 4 hints * 2 questions
    assert mission.npc is not None
    assert mission.rewards.xp > 0
    assert mission.completion_condition.required_value == 0.7


def test_boss_generator(router, sample_concept):
    c2 = Concept(concept_id="c_scope", name="Scope", description="Scope determines variable visibility.", difficulty=3)
    b_gen = BossGenerator(router)
    boss = b_gen.generate_boss_challenge("Python Fundamentals", [sample_concept, c2])

    assert len(boss.concept_ids) == 2
    assert len(boss.phases) == 2
    assert len(boss.questions) == 2
    assert boss.rewards.xp == 250
