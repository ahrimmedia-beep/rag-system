from app.domain.models import Chunk
from app.services.retrieval import RetrievalService
from tests.fakes import FakeEmbeddings, FakeVectorStore


def _store_with(*chunks: Chunk) -> FakeVectorStore:
    store = FakeVectorStore()
    emb = FakeEmbeddings()
    store.upsert(list(chunks), emb.embed_documents([c.text for c in chunks]))
    return store


def test_retrieve_returns_top_k():
    store = _store_with(
        Chunk(id="1", text="aaaa", metadata={}),
        Chunk(id="2", text="eeee", metadata={}),
    )
    svc = RetrievalService(FakeEmbeddings(), store, top_k=1)
    hits = svc.retrieve("aaaa")
    assert len(hits) == 1 and hits[0].chunk.id == "1"


def test_retrieve_applies_metadata_filter():
    store = _store_with(
        Chunk(id="1", text="aaaa", metadata={"section": "Deposits"}),
        Chunk(id="2", text="aaaa", metadata={"section": "Withdrawals"}),
    )
    svc = RetrievalService(FakeEmbeddings(), store, top_k=5)
    hits = svc.retrieve("aaaa", metadata_filter={"section": "Withdrawals"})
    assert [h.chunk.id for h in hits] == ["2"]


def test_retrieve_drops_hits_below_score_threshold():
    store = _store_with(Chunk(id="1", text="aaaa", metadata={}))
    svc = RetrievalService(FakeEmbeddings(), store, top_k=5, score_threshold=999.0)
    assert svc.retrieve("aaaa") == []
