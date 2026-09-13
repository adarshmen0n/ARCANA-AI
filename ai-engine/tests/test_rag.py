"""Unit tests for embeddings, vector store, and RAG subsystem."""

import pytest
from schemas.document import Chunk
from embeddings.engine import EmbeddingEngine
from retrieval.vector_store import VectorStore
from rag.context_builder import ContextBuilder
from rag.engine import RAGEngine
from providers.mock import MockEmbeddingProvider, MockLLMProvider
from providers.router import ProviderRouter


def test_embedding_cache():
    provider = MockEmbeddingProvider(dimension=64)
    engine = EmbeddingEngine(provider=provider)

    v1 = engine.embed_text("Operating Systems")
    assert engine.cache_misses == 1
    assert engine.cache_hits == 0

    v2 = engine.embed_text("Operating Systems")
    assert engine.cache_misses == 1
    assert engine.cache_hits == 1
    assert v1 == v2


def test_vector_store_filtering_and_ranking():
    store = VectorStore()
    embedding_engine = EmbeddingEngine(MockEmbeddingProvider(dimension=64))

    chunks = [
        Chunk(document_id="doc_os", chapter="OS", section="Processes", text="A process is in execution."),
        Chunk(document_id="doc_os", chapter="OS", section="Memory", text="Virtual memory paging algorithms."),
        Chunk(document_id="doc_py", chapter="Python", section="Syntax", text="Python uses indentation."),
    ]
    vecs = embedding_engine.embed_batch([c.text for c in chunks])
    store.add_chunks(chunks, vecs)

    assert store.total_chunks == 3

    # Search with chapter filter
    q_vec = embedding_engine.embed_text("memory management")
    results = store.search(q_vec, top_k=2, chapter="OS")
    assert len(results) <= 2
    for r in results:
        assert r.chunk.chapter == "OS"


def test_context_builder_citations():
    c1 = Chunk(chunk_id="chk_01", document_id="d1", chapter="Math", section="Algebra", text="Variables store numbers.", page_start=5)
    c2 = Chunk(chunk_id="chk_02", document_id="d1", chapter="Math", section="Geometry", text="Triangles have 3 sides.", page_start=12)

    from retrieval.vector_store import RetrievalResult
    results = [RetrievalResult(chunk=c1, score=0.9), RetrievalResult(chunk=c2, score=0.8)]

    context_str, chunk_ids = ContextBuilder.build_context(results)
    assert "chk_01" in chunk_ids
    assert "chk_02" in chunk_ids
    assert "Algebra, Page 5" in context_str


def test_rag_engine_grounded_answer():
    embedding_engine = EmbeddingEngine(MockEmbeddingProvider(dimension=64))
    vector_store = VectorStore()

    c = Chunk(chunk_id="chk_cpu", document_id="doc_1", chapter="OS", section="CPU", text="Round Robin uses time slices.")
    vec = embedding_engine.embed_text(c.text)
    vector_store.add_chunks([c], [vec])

    router = ProviderRouter(
        primary_provider=MockLLMProvider(),
        fallback_provider=MockLLMProvider(),
        embedding_provider=MockEmbeddingProvider(dimension=64),
    )

    rag = RAGEngine(vector_store=vector_store, embedding_engine=embedding_engine, provider_router=router)
    ans = rag.query("How does Round Robin schedule?", top_k=1)

    assert ans.query == "How does Round Robin schedule?"
    assert len(ans.source_chunk_ids) == 1
    assert ans.source_chunk_ids[0] == "chk_cpu"
    assert "MockLLM response" in ans.answer
