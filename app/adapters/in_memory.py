"""In-process, offline implementations of the `EmbeddingsProvider` and `VectorStore`
ports — no network calls. Real, shippable adapters (unlike test doubles under
`tests/`): used by the `eval/` harness and re-exported by `tests/fakes.py` so both
stay boundary-clean and importable from the Docker image, which excludes `tests/`.
"""

from app.domain.models import Chunk, RetrievedChunk


class DeterministicEmbeddings:
    """Deterministic 3-dim embeddings from character stats — no network."""

    def _vec(self, text: str) -> list[float]:
        t = text.lower()
        return [float(len(text)), float(t.count("a")), float(t.count("e"))]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._vec(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vec(text)


class InMemoryVectorStore:
    """In-process VectorStore: ranks by dot-product, with optional metadata filter."""

    def __init__(self) -> None:
        self._items: list[tuple[Chunk, list[float]]] = []
        self.ensured_dim: int | None = None

    def ensure_collection(self, dim: int) -> None:
        self.ensured_dim = dim

    def upsert(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        self._items.extend(zip(chunks, vectors, strict=True))

    def search(
        self, vector: list[float], top_k: int, metadata_filter: dict[str, object] | None = None
    ) -> list[RetrievedChunk]:
        def matches(c: Chunk) -> bool:
            if not metadata_filter:
                return True
            return all(c.metadata.get(k) == v for k, v in metadata_filter.items())

        def dot(a: list[float], b: list[float]) -> float:
            return sum(x * y for x, y in zip(a, b, strict=True))

        scored = [
            RetrievedChunk(chunk=c, score=dot(vector, v)) for c, v in self._items if matches(c)
        ]
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

    def health_check(self) -> bool:
        return True
