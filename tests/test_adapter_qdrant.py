from types import SimpleNamespace

import pytest

from app.adapters.vector_qdrant import QdrantVectorStore
from app.core.exceptions import KnowledgeBaseUnavailable
from app.domain.models import Chunk


class _FakeQdrant:
    def __init__(self) -> None:
        self.points: list = []
        self.created: str | None = None

    def collection_exists(self, name: str) -> bool:
        return self.created == name

    def create_collection(self, collection_name: str, vectors_config: object) -> None:
        self.created = collection_name

    def upsert(self, collection_name: str, points: list) -> None:
        self.points.extend(points)

    def query_points(
        self, collection_name: str, query, limit, query_filter=None, with_payload=True
    ):
        points = [SimpleNamespace(id="1", score=0.9, payload={"text": "hello", "lesson": "L1"})][
            :limit
        ]
        return SimpleNamespace(points=points)

    def get_collections(self) -> object:
        return SimpleNamespace(collections=[])


class _RaisingQdrant:
    """Every client call fails, simulating an unreachable/down Qdrant instance."""

    def collection_exists(self, name: str) -> bool:
        raise RuntimeError("connection refused")

    def create_collection(self, collection_name: str, vectors_config: object) -> None:
        raise RuntimeError("connection refused")

    def upsert(self, collection_name: str, points: list) -> None:
        raise RuntimeError("connection refused")

    def query_points(
        self, collection_name: str, query, limit, query_filter=None, with_payload=True
    ):
        raise RuntimeError("connection refused")

    def get_collections(self) -> object:
        raise RuntimeError("connection refused")


def test_qdrant_upsert_and_search_roundtrip():
    client = _FakeQdrant()
    store = QdrantVectorStore("http://x", "kb", client=client)
    store.ensure_collection(3)
    assert client.created == "kb"
    store.upsert([Chunk(id="1", text="hello", metadata={"lesson": "L1"})], [[1.0, 0.0, 0.0]])
    assert client.points and client.points[0].payload["text"] == "hello"
    hits = store.search([1.0, 0.0, 0.0], top_k=1)
    assert hits[0].chunk.text == "hello"
    assert hits[0].chunk.metadata["lesson"] == "L1"
    assert "text" not in hits[0].chunk.metadata


def test_qdrant_health_check_true_when_client_reachable():
    store = QdrantVectorStore("http://x", "kb", client=_FakeQdrant())
    assert store.health_check() is True


def test_qdrant_health_check_false_when_client_raises():
    store = QdrantVectorStore("http://x", "kb", client=_RaisingQdrant())
    assert store.health_check() is False


def test_qdrant_ensure_collection_raises_knowledge_base_unavailable():
    store = QdrantVectorStore("http://x", "kb", client=_RaisingQdrant())
    with pytest.raises(KnowledgeBaseUnavailable):
        store.ensure_collection(3)


def test_qdrant_upsert_raises_knowledge_base_unavailable():
    store = QdrantVectorStore("http://x", "kb", client=_RaisingQdrant())
    with pytest.raises(KnowledgeBaseUnavailable):
        store.upsert([Chunk(id="1", text="hello", metadata={})], [[1.0]])


def test_qdrant_search_raises_knowledge_base_unavailable():
    store = QdrantVectorStore("http://x", "kb", client=_RaisingQdrant())
    with pytest.raises(KnowledgeBaseUnavailable):
        store.search([1.0], top_k=1)
