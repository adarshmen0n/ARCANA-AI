"""Complete end-to-end ARCANA AI Brain Pipeline and Orchestrator.

Orchestrates the entire educational intelligence workflow from raw document
to fully validated Game Specification, recording granular stage latencies
and supporting asynchronous background execution.
"""

from concurrent.futures import ThreadPoolExecutor
import logging
import time
from typing import Callable, Dict, Optional, Tuple
from schemas.document import ExtractedDocument, Chunk
from schemas.knowledge import KnowledgeGraph
from schemas.learning_graph import LearningGraph
from schemas.game_spec import GameSpecification
from schemas.job import ProcessingJob, JobStatus
from schemas.base import generate_id, current_utc_time
from ingestion.engine import DocumentIngestionEngine
from preprocessing.cleaner import TextCleaner
from chunking.semantic_chunker import SemanticChunker
from embeddings.engine import EmbeddingEngine
from retrieval.vector_store import VectorStore
from knowledge.extractor import KnowledgeEngine
from learning_graph.graph import LearningGraphEngine
from game_specification.builder import GameSpecificationBuilder
from providers.router import ProviderRouter

logger = logging.getLogger("arcana.pipeline")


class PipelineResult:
    """Encapsulates the end-to-end output and stage timings of the Brain pipeline."""

    def __init__(
        self,
        document: ExtractedDocument,
        chunks: list[Chunk],
        knowledge_graph: KnowledgeGraph,
        learning_graph: LearningGraph,
        game_specification: GameSpecification,
        timings_ms: Dict[str, float],
    ):
        self.document = document
        self.chunks = chunks
        self.knowledge_graph = knowledge_graph
        self.learning_graph = learning_graph
        self.game_specification = game_specification
        self.timings_ms = timings_ms


class ArcanaBrainPipeline:
    """Master orchestrator for the complete ARCANA educational intelligence engine."""

    def __init__(self, provider_router: Optional[ProviderRouter] = None):
        self.router = provider_router or ProviderRouter()
        self.ingestion_engine = DocumentIngestionEngine()
        self.cleaner = TextCleaner()
        self.chunker = SemanticChunker()
        self.embedding_engine = EmbeddingEngine(self.router.embedding_provider)
        self.vector_store = VectorStore()
        self.knowledge_engine = KnowledgeEngine(self.router)
        self.game_spec_builder = GameSpecificationBuilder(self.router)

        self._jobs: Dict[str, ProcessingJob] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)

    def execute_sync(
        self,
        file_bytes: bytes,
        filename: str,
        subject: str = "Computer Science",
        campaign_title: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
    ) -> PipelineResult:
        """Execute the complete vertical slice synchronously with stage latency telemetry."""
        timings: Dict[str, float] = {}
        total_start = time.perf_counter()

        def update(stage: str, pct: int):
            if progress_callback:
                progress_callback(stage, pct)
            logger.info("[Pipeline] Stage: %s (%d%%)", stage, pct)

        # Stage 1: Ingestion & Format Extraction
        update("Extracting Document", 10)
        t0 = time.perf_counter()
        raw_doc = self.ingestion_engine.ingest(file_bytes, filename)
        timings["ingestion_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Stage 2: Preprocessing & Cleaning
        update("Cleaning Content", 25)
        t0 = time.perf_counter()
        clean_doc = self.cleaner.preprocess_document(raw_doc)
        timings["cleaning_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Stage 3: Semantic Chunking
        update("Generating Semantic Chunks", 40)
        t0 = time.perf_counter()
        chunks = self.chunker.chunk_document(clean_doc)
        timings["chunking_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Stage 4: Embeddings & Vector Store Indexing
        update("Indexing Embeddings", 55)
        t0 = time.perf_counter()
        if chunks:
            vectors = self.embedding_engine.embed_batch([c.text for c in chunks])
            self.vector_store.add_chunks(chunks, vectors)
        timings["embedding_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Stage 5: Knowledge Extraction (Concepts & Dependencies)
        update("Extracting Knowledge Graph", 70)
        t0 = time.perf_counter()
        kg = self.knowledge_engine.build_knowledge_graph(
            chunks=chunks,
            document_id=clean_doc.document_id,
            subject=subject,
        )
        timings["knowledge_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Stage 6: Learning Graph DAG & Topological Order
        update("Constructing Learning Graph DAG", 80)
        t0 = time.perf_counter()
        lg = LearningGraphEngine.build_from_knowledge_graph(kg)
        timings["learning_graph_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        # Stage 7: Game Specification Compilation & Multi-Tier Validation
        update("Building & Validating Game Specification", 95)
        t0 = time.perf_counter()
        title = campaign_title or f"{subject} Quest"
        spec = self.game_spec_builder.build_specification(
            learning_graph=lg,
            concepts=kg.concepts,
            campaign_title=title,
        )
        timings["game_spec_ms"] = round((time.perf_counter() - t0) * 1000, 2)

        timings["total_pipeline_ms"] = round((time.perf_counter() - total_start) * 1000, 2)
        update("Ready", 100)

        logger.info(
            "Pipeline successfully completed in %.2fms: %d concepts, %d chunks",
            timings["total_pipeline_ms"],
            len(kg.concepts),
            len(chunks),
        )

        return PipelineResult(
            document=clean_doc,
            chunks=chunks,
            knowledge_graph=kg,
            learning_graph=lg,
            game_specification=spec,
            timings_ms=timings,
        )

    def submit_async_job(
        self,
        file_bytes: bytes,
        filename: str,
        subject: str = "Computer Science",
        campaign_title: Optional[str] = None,
    ) -> str:
        """Enqueues an asynchronous processing job and immediately returns a job_id."""
        job_id = generate_id("job")
        job = ProcessingJob(
            job_id=job_id,
            status=JobStatus.QUEUED,
            progress_percent=0,
            current_stage="Queued",
        )
        self._jobs[job_id] = job

        def worker():
            def cb(stage: str, pct: int):
                job.current_stage = stage
                job.progress_percent = pct
                job.status = JobStatus.PROCESSING if pct < 100 else JobStatus.READY
                job.updated_at = current_utc_time().isoformat()

            try:
                result = self.execute_sync(
                    file_bytes=file_bytes,
                    filename=filename,
                    subject=subject,
                    campaign_title=campaign_title,
                    progress_callback=cb,
                )
                job.status = JobStatus.READY
                job.progress_percent = 100
                job.current_stage = "Ready"
                job.result = result.game_specification.model_dump()
                job.document_id = result.document.document_id
                job.updated_at = current_utc_time().isoformat()
            except Exception as e:
                logger.error("Async job %s failed: %s", job_id, e)
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.current_stage = "Failed"
                job.updated_at = current_utc_time().isoformat()

        self._executor.submit(worker)
        return job_id

    def get_job(self, job_id: str) -> Optional[ProcessingJob]:
        """Retrieve the live status and result of an asynchronous job."""
        return self._jobs.get(job_id)
