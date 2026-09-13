"""Unit tests for Groq LLM Provider and streaming parser."""

import json
from unittest.mock import patch, MagicMock
import pytest
from pydantic import BaseModel
from providers.groq_provider import GroqProvider


class MissionObjective(BaseModel):
    title: str
    difficulty: int
    mechanic: str


def test_groq_provider_no_key():
    provider = GroqProvider(api_key="")
    assert provider.health_check() is False
    with pytest.raises(RuntimeError, match="GROQ_API_KEY is not configured"):
        provider.generate("Hello world")


@patch("httpx.Client.post")
def test_groq_provider_generate(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "Groq completed response successfully.",
                }
            }
        ]
    }
    mock_post.return_value = mock_resp

    provider = GroqProvider(api_key="mock_groq_key", model_name="openai/gpt-oss-20b")
    result = provider.generate("Explain concurrency")
    assert "Groq completed response" in result
    assert provider.model_name == "openai/gpt-oss-20b"


@patch("httpx.Client.post")
def test_groq_provider_generate_structured(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": json.dumps({
                        "title": "Master Concurrency",
                        "difficulty": 3,
                        "mechanic": "puzzle"
                    }),
                }
            }
        ]
    }
    mock_post.return_value = mock_resp

    provider = GroqProvider(api_key="mock_groq_key")
    obj = provider.generate_structured("Generate mission", response_model=MissionObjective)
    assert isinstance(obj, MissionObjective)
    assert obj.title == "Master Concurrency"
    assert obj.difficulty == 3
    assert obj.mechanic == "puzzle"


@pytest.mark.anyio
async def test_groq_provider_stream():
    provider = GroqProvider(api_key="mock_groq_key")

    sse_lines = [
        'data: {"choices": [{"delta": {"content": "The "}}]}',
        'data: {"choices": [{"delta": {"content": "quick "}}]}',
        'data: {"choices": [{"delta": {"content": "fox"}}]}',
        'data: [DONE]',
    ]

    class MockAsyncResponse:
        status_code = 200
        async def aiter_lines(self):
            for line in sse_lines:
                yield line
        async def aread(self):
            return b""

    class MockStreamContext:
        async def __aenter__(self):
            return MockAsyncResponse()
        async def __aexit__(self, exc_type, exc, tb):
            pass

    with patch("httpx.AsyncClient.stream", return_value=MockStreamContext()):
        tokens = []
        async for token in provider.stream("Test prompt"):
            tokens.append(token)

        assert "".join(tokens) == "The quick fox"
