"""Unit tests for Preprocessing and Semantic Chunking Subsystems."""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure ai-engine-adarsh is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.preprocessing.normalizer import (
    normalize_text,
    clean_whitespace,
    repair_hyphenation,
    remove_document_artifacts,
)
from app.preprocessing.detector import detect_sections
from app.chunking.models import ChunkingConfig
from app.chunking.chunker import SemanticChunker, split_into_sentences
from app.ingestion.service import ingestion_service
from app.chunking.service import chunking_service

client = TestClient(app)


def test_repair_hyphenation():
    """Verify broken words across linebreaks are repaired."""
    raw = "CPU sched-\nuling algorithms determine how pro-\ncesses run."
    expected = "CPU scheduling algorithms determine how processes run."
    assert repair_hyphenation(raw) == expected


def test_clean_whitespace():
    """Verify excessive spaces and blank lines are collapsed."""
    raw = "First   paragraph.\n\n\n\n\nSecond paragraph.\t\tThird item."
    cleaned = clean_whitespace(raw)
    assert "\n\n\n" not in cleaned
    assert "First paragraph." in cleaned
    assert "Second paragraph." in cleaned


def test_remove_document_artifacts():
    """Verify page numbers and header noise are removed."""
    raw = "Header text\nPage 4 of 100\n- 42 -\nUseful educational content."
    cleaned = remove_document_artifacts(raw)
    assert "Page 4 of 100" not in cleaned
    assert "- 42 -" not in cleaned
    assert "Useful educational content." in cleaned


def test_normalize_text_pipeline():
    """Verify master normalization pipeline cleans unicode, hyphens, and whitespace."""
    raw = "Chapter 1:\u00a0Process Manage-\nment.\n\n\n\nPage 1\nOperating systems execute tasks."
    normalized = normalize_text(raw)
    assert "Manage- ment" not in normalized
    assert "Management." in normalized
    assert "Page 1" not in normalized
    assert "\u00a0" not in normalized


def test_detect_sections():
    """Verify chapter and numbered sections are identified accurately."""
    raw = (
        "CHAPTER 5: CPU SCHEDULING\n"
        "CPU scheduling is the basis of multi-programmed operating systems.\n\n"
        "5.1 Basic Concepts\n"
        "By switching the CPU among processes, the OS can make the computer more productive.\n\n"
        "5.2 Scheduling Criteria\n"
        "Different CPU scheduling algorithms have different properties."
    )
    sections = detect_sections(raw)

    assert len(sections) == 3
    assert "CHAPTER 5" in sections[0].heading
    assert sections[1].heading == "Basic Concepts"
    assert sections[1].section_number == "5.1"
    assert sections[2].heading == "Scheduling Criteria"
    assert sections[2].section_number == "5.2"


def test_split_into_sentences():
    """Verify text is split along sentence boundaries without corrupting abbreviations."""
    text = "FCFS is non-preemptive. What is the Convoy Effect? It occurs when short jobs wait!"
    sentences = split_into_sentences(text)
    assert len(sentences) == 3
    assert sentences[0] == "FCFS is non-preemptive."
    assert sentences[1] == "What is the Convoy Effect?"
    assert sentences[2] == "It occurs when short jobs wait!"


def test_semantic_chunker_basic():
    """Verify SemanticChunker generates chunks with metadata and estimated tokens."""
    raw = (
        "Chapter 5: CPU Scheduling\n"
        "5.1 FCFS Scheduling\n"
        "By far the simplest CPU-scheduling algorithm is the first-come, first-served (FCFS) algorithm. "
        "With this scheme, the process that requests the CPU first is allocated the CPU first. "
        "The implementation of the FCFS policy is easily managed with a FIFO queue."
    )
    sections = detect_sections(raw)
    chunker = SemanticChunker(ChunkingConfig(chunk_size_chars=200, chunk_overlap_chars=40))
    chunks = chunker.chunk_sections("doc-test-123", sections)

    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk.document_id == "doc-test-123"
        assert chunk.chunk_id.startswith("chk-doctest1-")
        assert chunk.token_count > 0
        assert len(chunk.text) > 0


def test_api_chunking_workflow():
    """Verify HTTP flow: upload document -> trigger chunking -> get chunks -> get individual chunk."""
    content = (
        b"Chapter 5: CPU Scheduling\n\n"
        b"5.1 Overview\n"
        b"In a single-processor system, only one process can run at a time.\n\n"
        b"5.2 FCFS Scheduling\n"
        b"First-Come First-Served scheduling allocates the CPU in order of process arrival."
    )

    # 1. Upload
    upload_res = client.post(
        "/api/v1/documents/upload",
        files={"file": ("cpu_ch5.txt", content, "text/plain")},
    )
    assert upload_res.status_code == 202
    doc_id = upload_res.json()["document_id"]

    # 2. Trigger Chunking
    chunk_res = client.post(f"/api/v1/documents/{doc_id}/chunks")
    assert chunk_res.status_code == 200
    chunk_data = chunk_res.json()
    assert chunk_data["total_chunks"] >= 2
    assert chunk_data["total_tokens_estimated"] > 0

    first_chunk_id = chunk_data["chunks"][0]["chunk_id"]

    # 3. Retrieve All Chunks
    list_res = client.get(f"/api/v1/documents/{doc_id}/chunks")
    assert list_res.status_code == 200
    chunks_list = list_res.json()
    assert len(chunks_list) == chunk_data["total_chunks"]

    # 4. Retrieve Specific Chunk by ID
    single_res = client.get(f"/api/v1/chunks/{first_chunk_id}")
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert single_data["chunk_id"] == first_chunk_id
    assert single_data["document_id"] == doc_id
