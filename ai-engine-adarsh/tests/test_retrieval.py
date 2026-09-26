"""Unit and integration tests for Embeddings and Vector Retrieval."""

import math
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure ai-engine-adarsh is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.embeddings.mock_provider import MockEmbeddingProvider
from app.embeddings.models import EmbeddedChunk
from app.retrieval.models import RetrievalQuery
from app.retrieval.vector_store import InMemoryVectorStore
from app.retrieval.service import retrieval_service

client = TestClient(app)


def test_mock_embedding_provider_properties():
    """Verify mock provider generates normalized, deterministic vectors with semantic affinity."""
    provider = MockEmbeddingProvider(dimension=128)
    assert provider.dimension == 128

    v1 = provider.embed_text("CPU Scheduling FCFS Algorithm")
    v2 = provider.embed_text("CPU Scheduling FCFS Algorithm")
    v3 = provider.embed_text("Photosynthesis in green plants")

    # Determinism
    assert v1 == v2

    # L2 Unit Norm
    norm = math.sqrt(sum(x * x for x in v1))
    assert abs(norm - 1.0) < 1e-4

    # Dot product similarity (v1 vs v2 == 1.0)
    sim_identical = sum(a * b for a, b in zip(v1, v2))
    assert abs(sim_identical - 1.0) < 1e-4

    # Dot product similarity (related vs unrelated)
    sim_unrelated = sum(a * b for a, b in zip(v1, v3))
    assert sim_unrelated < sim_identical


def test_in_memory_vector_store():
    """Verify vector store indexing, thresholding, and document isolation."""
    store = InMemoryVectorStore()
    provider = MockEmbeddingProvider(dimension=64)

    chunk_fcfs = EmbeddedChunk(
        chunk_id="chk-001",
        document_id="doc-os",
        text="First-Come First-Served algorithm suffers from Convoy Effect.",
        embedding=provider.embed_text("First-Come First-Served algorithm suffers from Convoy Effect."),
        heading="FCFS Scheduling",
        page_number=1,
    )
    chunk_plants = EmbeddedChunk(
        chunk_id="chk-002",
        document_id="doc-bio",
        text="Chloroplasts absorb sunlight to synthesize glucose.",
        embedding=provider.embed_text("Chloroplasts absorb sunlight to synthesize glucose."),
        heading="Photosynthesis",
        page_number=1,
    )

    store.add_chunks([chunk_fcfs, chunk_plants])
    assert store.count_chunks() == 2
    assert store.count_chunks("doc-os") == 1

    # Search for FCFS query
    q_vec = provider.embed_text("FCFS Convoy Effect")
    results, searched = store.search(q_vec, document_id="doc-os", top_k=5, threshold=0.1)

    assert len(results) == 1
    assert results[0][0].chunk_id == "chk-001"
    assert results[0][1] > 0.5


def test_api_retrieval_query():
    """Verify HTTP end-to-end flow: Upload document -> Index vectors -> Semantic query."""
    doc_text = (
        b"Chapter 5: CPU Scheduling\n\n"
        b"5.1 FCFS Scheduling\n"
        b"In First-Come, First-Served scheduling, the process requesting CPU first gets it first. "
        b"A serious disadvantage is the Convoy Effect where small processes wait behind a massive CPU burst.\n\n"
        b"5.2 Round Robin Scheduling\n"
        b"Round Robin assigns a fixed time quantum per process with preemption."
    )

    # 1. Upload
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("os_sched.txt", doc_text, "text/plain")},
    )
    assert upload_res.status_code == 202
    doc_id = upload_res.json()["document_id"]

    # 2. Index Document Chunks
    index_res = client.post(f"/api/v1/documents/{doc_id}/index")
    assert index_res.status_code == 200
    assert index_res.json()["chunks_indexed"] >= 2

    # 3. Query Knowledge Base for Convoy Effect
    query_payload = {
        "query": "What causes the Convoy Effect in FCFS?",
        "document_id": doc_id,
        "top_k": 3,
        "similarity_threshold": 0.2,
    }
    query_res = client.post("/api/v1/retrieval/query", json=query_payload)
    assert query_res.status_code == 200
    data = query_res.json()

    assert data["retrieved_count"] > 0
    top_chunk = data["results"][0]
    assert "FCFS" in top_chunk["text"] or "Convoy Effect" in top_chunk["text"]
    assert top_chunk["similarity_score"] > 0.3
    assert top_chunk["document_id"] == doc_id
