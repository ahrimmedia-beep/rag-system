from typing import Any

from app.core.exceptions import KnowledgeBaseUnavailable
from app.domain.models import Chunk, RetrievedChunk


class QdrantVectorStore:
    def __init__(self, url: str, collection: str, client: Any | None = None) -> None:
        if client is None:
            from qdrant_client import QdrantClient

            client = QdrantClient(url=url)
        self._client = client
        self._collection = collection

    def ensure_collection(self, dim: int) -> None:
        from qdrant_client.models import Distance, VectorParams

        try:
            if not self._client.collection_exists(self._collection):
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
        except Exception as e:
            raise KnowledgeBaseUnavailable(str(e)) from e

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(id=c.id, vector=v, payload={"text": c.text, **c.metadata})
            for c, v in zip(chunks, vectors, strict=True)
        ]
        try:
            self._client.upsert(collection_name=self._collection, points=points)
        except Exception as e:
            raise KnowledgeBaseUnavailable(str(e)) from e

    def search(
        self,
        vector: list[float],
        top_k: int,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]:
        query_filter = None
        if metadata_filter:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            query_filter = Filter(
                must=[
                    FieldCondition(key=k, match=MatchValue(value=v))  # type: ignore[arg-type]
                    for k, v in metadata_filter.items()
                ]
            )
        try:
            response = self._client.query_points(
                collection_name=self._collection,
                query=vector,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True,
            )
        except Exception as e:
            raise KnowledgeBaseUnavailable(str(e)) from e
        results: list[RetrievedChunk] = []
        for h in response.points:
            payload = dict(h.payload or {})
            text = str(payload.pop("text", ""))
            results.append(
                RetrievedChunk(
                    chunk=Chunk(id=str(h.id), text=text, metadata=payload), score=h.score
                )
            )
        return results

    def health_check(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception:
            return False
