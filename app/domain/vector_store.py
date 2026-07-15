from typing import Protocol

from app.domain.models import Chunk, RetrievedChunk


class VectorStore(Protocol):
    def ensure_collection(self, dim: int) -> None: ...
    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...
    def search(
        self,
        vector: list[float],
        top_k: int,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievedChunk]: ...
    def health_check(self) -> bool: ...
