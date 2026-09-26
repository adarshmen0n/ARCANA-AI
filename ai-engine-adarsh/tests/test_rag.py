"""Unit and integration tests for RAG Subsystem and Grounded Generation."""

import os
import sys
import pytest
from pydantic import BaseModel
from fastapi.testclient import TestClient

# Ensure ai-engine-adarsh is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.providers.mock_provider import MockLLMProvider
from app.retrieval.models import RetrievedChunk
from app.rag.context_builder import ContextBuilder
from app.rag.models import RAGQueryRequest
from app.rag.service import rag_service

client = TestClient(app)


class SampleStructuredOutput(BaseModel):
    title: str
    difficulty: int
    summary: str


def test_mock_llm_provider_generation():
    """Verify mock LLM provider generates text and structured schemas cleanly."""
    provider = MockLLMProvider()

    # Text Generation
    prompt = "Question: What is FCFS Scheduling?\nContext: [Chunk: chk-cpu-001] FCFS runs jobs in order."
    response = provider.generate_text(prompt)
    assert "FCFS Scheduling" in response
    assert "[Source: chk-cpu-001]" in response

    # Structured Generation
    structured = provider.generate_structured("Generate lesson", SampleStructuredOutput)
    assert isinstance(structured, SampleStructuredOutput)
    assert structured.title.startswith("Mock")
    assert structured.difficulty == 1


def test_context_builder_budget_enforcement():
    """Verify ContextBuilder stays within token budgets."""
    chunks = [
        RetrievedChunk(
            chunk_id=f"chk-{i}",
            document_id="doc-1",
            text="Detailed algorithmic explanation of CPU scheduling and process dispatching. " * 5,
            heading="CPU Scheduling",
            page_number=i,
            similarity_score=0.8,
        )
        for i in range(10)
    ]

    # Set small token budget allowing only ~2 chunks
    formatted, included, tokens = ContextBuilder.assemble(chunks, max_token_budget=150)

    assert len(included) < len(chunks)
    assert tokens <= 250
    assert "[Chunk: chk-0]" in formatted


def test_rag_service_with_context():
    """Verify RAGService produces grounded answer with citations."""
    doc_text = (
        b"Chapter 5: CPU Scheduling\n\n"
        b"5.1 First-Come First-Served\n"
        b"The First-Come, First-Served (FCFS) algorithm is the simplest scheduling algorithm. "
        b"A disadvantage of FCFS is the Convoy Effect, where small processes wait behind a massive compute job."
    )

    # Upload document
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("os_ch5_rag.txt", doc_text, "text/plain")},
    )
    assert upload_res.status_code == 202
    doc_id = upload_res.json()["document_id"]

    # Request RAG Answer
    req = RAGQueryRequest(
        query="What is the Convoy Effect in FCFS?",
        document_id=doc_id,
        max_context_chunks=3,
        similarity_threshold=0.1,
    )
    answer = rag_service.answer_query(req)

    assert answer.grounded is True
    assert len(answer.citations) > 0
    assert answer.citations[0].chunk_id.startswith("chk-")
    assert answer.confidence_score > 0.0
    assert answer.latency_ms > 0.0


def test_api_rag_endpoint():
    """Verify POST /api/v1/rag/answer returns valid JSON matching RAGAnswer schema."""
    doc_text = (
        b"Chapter 5: CPU Scheduling\n\n"
        b"5.2 Shortest Job First\n"
        b"Shortest Job First (SJF) scheduling associates each process with its next CPU burst length. "
        b"SJF is optimal in minimizing average waiting time."
    )

    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("sjf_notes.txt", doc_text, "text/plain")},
    )
    doc_id = upload_res.json()["document_id"]

    payload = {
        "query": "Why is Shortest Job First optimal?",
        "document_id": doc_id,
        "max_context_chunks": 2,
        "similarity_threshold": 0.1,
    }

    res = client.post("/api/v1/rag/answer", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "answer" in data
    assert len(data["answer"]) > 10
    assert data["grounded"] is True
    assert len(data["citations"]) > 0
    assert "latency_ms" in data
