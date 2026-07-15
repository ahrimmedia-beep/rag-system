from typing import Any

from fastapi.testclient import TestClient

from app.api.dependencies import get_ingestion_service, get_rag_agent_service, get_vector_store
from app.core.exceptions import KnowledgeBaseUnavailable
from app.domain.models import Answer, Source
from app.main import create_app


class _StubIngestion:
    def ingest(self, text: str, metadata: dict) -> int:
        return 3


class _StubAgent:
    def answer(self, session_id: str, question: str) -> Answer:
        return Answer(answer="grounded", sources=[Source("l1.txt", "Lesson 1", "12:34", 0.9)])


class _StubAgentUnavailable:
    def answer(self, session_id: str, question: str) -> Answer:
        raise KnowledgeBaseUnavailable("qdrant unreachable")


class _StubStore:
    def __init__(self, healthy: bool = True) -> None:
        self._healthy = healthy

    def health_check(self) -> bool:
        return self._healthy


def _client(agent: Any = None, store_healthy: bool = True) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_ingestion_service] = lambda: _StubIngestion()
    app.dependency_overrides[get_rag_agent_service] = lambda: agent or _StubAgent()
    app.dependency_overrides[get_vector_store] = lambda: _StubStore(store_healthy)
    return TestClient(app)


def test_health():
    r = _client().get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "qdrant": True}


def test_health_returns_503_when_store_unhealthy():
    r = _client(store_healthy=False).get("/health")
    assert r.status_code == 503
    assert r.json() == {"status": "ok", "qdrant": False}


def test_ingest_endpoint():
    r = _client().post("/ingest", json={"text": "hello world", "source": "l1.txt"})
    assert r.status_code == 200
    assert r.json() == {"ingested_chunks": 3, "source": "l1.txt"}


def test_ask_endpoint_returns_answer_and_sources():
    r = _client().post("/ask", json={"session_id": "s1", "question": "how?"})
    assert r.status_code == 200
    body = r.json()
    assert body["answer"] == "grounded"
    assert body["sources"][0]["lesson"] == "Lesson 1"


def test_ask_validation_error_on_empty_question():
    assert _client().post("/ask", json={"session_id": "s1", "question": ""}).status_code == 422


def test_ask_returns_503_when_knowledge_base_unavailable():
    r = _client(agent=_StubAgentUnavailable()).post(
        "/ask", json={"session_id": "s1", "question": "how?"}
    )
    assert r.status_code == 503
    assert r.json() == {"detail": "knowledge base unavailable"}
