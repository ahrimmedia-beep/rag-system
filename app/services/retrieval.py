from app.domain.embeddings import EmbeddingsProvider
from app.domain.models import RetrievedChunk
from app.domain.vector_store import VectorStore


class RetrievalService:
    def __init__(
        self,
        embeddings: EmbeddingsProvider,
        store: VectorStore,
        top_k: int = 5,
        score_threshold: float = 0.0,
    ) -> None:
        self._embeddings = embeddings
        self._store = store
        self._top_k = top_k
        self._score_threshold = score_threshold

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        vector = self._embeddings.embed_query(query)
        hits = self._store.search(vector, top_k or self._top_k, metadata_filter)
        return [h for h in hits if h.score >= self._score_threshold]
