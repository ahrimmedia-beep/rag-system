from app.services.ingestion import IngestionService
from tests.fakes import FakeEmbeddings, FakeVectorStore


def test_ingest_splits_embeds_and_upserts():
    store = FakeVectorStore()
    svc = IngestionService(
        FakeEmbeddings(), store, embeddings_dim=3, chunk_size=20, chunk_overlap=5
    )
    n = svc.ingest("word " * 40, {"source": "lesson1.txt", "lesson": "Lesson 1"})
    assert n > 1
    hits = store.search(FakeEmbeddings().embed_query("word"), top_k=100)
    assert len(hits) == n
    assert hits[0].chunk.metadata["source"] == "lesson1.txt"
    assert "chunk_index" in hits[0].chunk.metadata


def test_ingest_ensures_collection_with_configured_dim():
    store = FakeVectorStore()
    svc = IngestionService(FakeEmbeddings(), store, embeddings_dim=3)
    svc.ingest("hello world", {"source": "x"})
    assert store.ensured_dim == 3


def test_ingest_empty_text_returns_zero():
    store = FakeVectorStore()
    svc = IngestionService(FakeEmbeddings(), store, embeddings_dim=3)
    assert svc.ingest("", {"source": "x"}) == 0
