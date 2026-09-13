"""Integration test proving the FIRST VERTICAL SLICE of the ARCANA AI Brain.

Validates the complete pipeline:
PDF -> Extraction -> Cleaning -> Chunking -> Concepts -> Learning Graph ->
Learning Objective -> Mission -> Multi-Tier Validation -> Game Specification.
"""

import io
import time
import pytest
from pypdf import PdfWriter
from orchestration.pipeline import ArcanaBrainPipeline
from schemas.job import JobStatus
from providers.mock import MockLLMProvider, MockEmbeddingProvider
from providers.router import ProviderRouter


def _create_sample_educational_pdf() -> bytes:
    """Create a multi-page PDF with educational content."""
    writer = PdfWriter()

    # We can write pages or text
    # In pypdf, we add blank pages or text
    p1 = writer.add_blank_page(width=300, height=300)
    p2 = writer.add_blank_page(width=300, height=300)

    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_first_vertical_slice_complete():
    # Setup mock router for deterministic test
    router = ProviderRouter(
        primary_provider=MockLLMProvider(),
        fallback_provider=MockLLMProvider(),
        embedding_provider=MockEmbeddingProvider(dimension=64),
    )
    pipeline = ArcanaBrainPipeline(provider_router=router)

    # Use educational text content for deterministic multi-concept extraction
    content = (
        "# Operating Systems: Process Synchronization\n\n"
        "## Critical Section Problem\n"
        "A critical section is a piece of code that accesses shared resources. "
        "Only one process may execute in its critical section at a time.\n\n"
        "## Semaphores\n"
        "A semaphore is a synchronization tool that provides integer counters "
        "with wait and signal operations to prevent race conditions.\n\n"
        "## Deadlock Prevention\n"
        "Deadlock occurs when processes hold resources while waiting for others. "
        "Prevention eliminates one of the four Coffman conditions.\n"
    ).encode("utf-8")

    result = pipeline.execute_sync(
        file_bytes=content,
        filename="process_sync.txt",
        subject="Operating Systems",
        campaign_title="Conquering Concurrency",
    )

    # Verify Stage 1 & 2: Document & Cleaning
    assert result.document.filename == "process_sync.txt"
    assert len(result.document.sections) >= 3

    # Verify Stage 3: Semantic Chunking
    assert len(result.chunks) >= 3
    assert result.chunks[0].chunking_version == "1.0"

    # Verify Stage 4: Embeddings in Vector Store
    assert pipeline.vector_store.total_chunks >= 3

    # Verify Stage 5: Knowledge Graph
    assert len(result.knowledge_graph.concepts) >= 3
    concept_names = [c.name for c in result.knowledge_graph.concepts]
    assert "Critical Section Problem" in concept_names
    assert "Semaphores" in concept_names

    # Verify Stage 6: Learning Graph DAG
    lg = result.learning_graph
    assert lg.is_acyclic is True
    assert len(lg.topological_order) >= 3
    # Critical Section Problem should be before Deadlock Prevention
    assert lg.topological_order.index(result.knowledge_graph.concepts[0].concept_id) < \
           lg.topological_order.index(result.knowledge_graph.concepts[-1].concept_id)

    # Verify Stage 7: Game Specification Contract (for Dasarth's Game Engine)
    spec = result.game_specification
    assert spec.schema_version == "1.0"
    assert spec.campaign.title == "Conquering Concurrency"
    assert len(spec.campaign.chapters) >= 1

    first_mission = spec.campaign.chapters[0].missions[0]
    assert first_mission.mechanic is not None
    assert len(first_mission.questions) >= 1
    assert first_mission.npc is not None
    assert first_mission.rewards.xp > 0

    # Verify Granular Latency Metrics
    assert "ingestion_ms" in result.timings_ms
    assert "cleaning_ms" in result.timings_ms
    assert "chunking_ms" in result.timings_ms
    assert "embedding_ms" in result.timings_ms
    assert "knowledge_ms" in result.timings_ms
    assert "learning_graph_ms" in result.timings_ms
    assert "game_spec_ms" in result.timings_ms
    assert "total_pipeline_ms" in result.timings_ms
    assert result.timings_ms["total_pipeline_ms"] > 0


def test_async_job_lifecycle():
    router = ProviderRouter(
        primary_provider=MockLLMProvider(),
        embedding_provider=MockEmbeddingProvider(dimension=64),
    )
    pipeline = ArcanaBrainPipeline(provider_router=router)

    content = b"# Python Basics\n\n## Variables\nVariables store data.\n"
    job_id = pipeline.submit_async_job(content, "basics.txt", subject="Python")

    assert job_id.startswith("job_")

    # Poll until ready or timeout
    for _ in range(50):
        job = pipeline.get_job(job_id)
        assert job is not None
        if job.status == JobStatus.READY:
            break
        time.sleep(0.05)

    final_job = pipeline.get_job(job_id)
    assert final_job.status == JobStatus.READY
    assert final_job.progress_percent == 100
    assert final_job.result is not None
    assert final_job.result["schema_version"] == "1.0"
