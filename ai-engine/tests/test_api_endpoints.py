"""Integration tests for all ARCANA AI Brain REST API endpoints."""

import time
import pytest


@pytest.mark.anyio
async def test_process_text_async_and_job_status(async_client):
    # Step 1: Submit processing job
    payload = {
        "text": "# Operating Systems\n## Virtual Memory\nPaging maps virtual to physical addresses.\n",
        "filename": "memory.txt",
        "subject": "Operating Systems",
        "async_mode": True,
    }
    res = await async_client.post("/api/v1/documents/process-text", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "async"
    assert "job_id" in data
    job_id = data["job_id"]

    # Step 2: Query job status
    job_res = await async_client.get(f"/api/v1/jobs/{job_id}")
    assert job_res.status_code == 200
    job_data = job_res.json()
    assert job_data["job_id"] == job_id
    assert job_data["status"] in {"QUEUED", "PROCESSING", "READY"}


@pytest.mark.anyio
async def test_process_text_sync(async_client):
    payload = {
        "text": "# Python Essentials\n## Functions\nFunctions structure modular code.\n",
        "filename": "functions.txt",
        "subject": "Python",
        "async_mode": False,
    }
    res = await async_client.post("/api/v1/documents/process-text", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["mode"] == "sync"
    assert data["specification"] is not None
    assert data["specification"]["schema_version"] == "1.0"
    assert "total_pipeline_ms" in data["timings_ms"]


@pytest.mark.anyio
async def test_rag_query_endpoint(async_client):
    payload = {
        "query": "How does virtual memory paging work?",
        "top_k": 2,
    }
    res = await async_client.post("/api/v1/rag/query", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == payload["query"]
    assert "answer" in data
    assert "source_chunk_ids" in data


@pytest.mark.anyio
async def test_tutor_endpoint(async_client):
    payload = {
        "question": "What is the difference between processes and threads?",
        "student_state": {
            "student_id": "stu_api_test",
            "current_level": 2,
        },
    }
    res = await async_client.post("/api/v1/tutor/ask", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert data["adapted_for_level"] == 2
    assert "suggested_followup" in data


@pytest.mark.anyio
async def test_analytics_events_endpoint(async_client):
    payload = {
        "state": {
            "student_id": "stu_telemetry",
            "current_level": 1,
            "total_xp": 0,
            "total_coins": 0,
            "masteries": {},
        },
        "events": [
            {
                "student_id": "stu_telemetry",
                "mission_id": "m_01",
                "concept_id": "c_variables",
                "is_correct": True,
                "hints_used": 0,
                "response_time_seconds": 5.2,
            }
        ],
    }
    res = await async_client.post("/api/v1/analytics/events", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["updated_state"]["total_xp"] == 20
    assert data["next_action"]["action_type"] in {"learn", "practice", "advance", "revision", "boss"}
