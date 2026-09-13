"""Tests for providers, fallback routing, and mock engines."""

import numpy as np
import pytest
from pydantic import BaseModel
from providers.mock import MockEmbeddingProvider, MockLLMProvider
from providers.router import ProviderRouter


class SampleObjective(BaseModel):
    title: str
    difficulty: int
    is_active: bool


def test_mock_embedding_provider_determinism():
    provider = MockEmbeddingProvider(dimension=128)
    vec1 = provider.embed_text("Variables in Python")
    vec2 = provider.embed_text("Variables in Python")
    vec3 = provider.embed_text("Loops in Python")

    assert len(vec1) == 128
    # Exact match for identical input
    assert vec1 == vec2
    # Different input produces different vector
    assert vec1 != vec3

    # Normalized to unit length (L2 norm ~ 1.0)
    norm = np.linalg.norm(np.array(vec1))
    assert pytest.approx(norm, 0.001) == 1.0


def test_mock_llm_structured_output():
    provider = MockLLMProvider()
    res = provider.generate_structured("Explain loops", response_model=SampleObjective)
    assert isinstance(res, SampleObjective)
    assert res.difficulty == 2
    assert res.is_active is True


def test_provider_router_fallback():
    # Primary configured to fail, Fallback configured to succeed
    failing_primary = MockLLMProvider(model_name="failing-primary", should_fail=True)
    working_fallback = MockLLMProvider(model_name="working-fallback", should_fail=False)

    router = ProviderRouter(
        primary_provider=failing_primary,
        fallback_provider=working_fallback,
        max_retries=2,
        initial_backoff_sec=0.01,
    )

    output = router.generate("What is a compiler?")
    assert "MockLLM response" in output
    assert failing_primary.call_count == 2
    assert working_fallback.call_count == 1


def test_provider_router_three_tier_cascade():
    # Tier 1 fails, Tier 2 fails, Tier 3 succeeds
    tier1 = MockLLMProvider(model_name="tier1-gemini", should_fail=True)
    tier2 = MockLLMProvider(model_name="tier2-groq", should_fail=True)
    tier3 = MockLLMProvider(model_name="tier3-grounded", should_fail=False)

    router = ProviderRouter(
        providers=[tier1, tier2, tier3],
        max_retries=2,
        initial_backoff_sec=0.01,
    )

    result = router.generate("What is a deadlock?")
    assert "MockLLM response" in result
    assert tier1.call_count == 2
    assert tier2.call_count == 2
    assert tier3.call_count == 1

