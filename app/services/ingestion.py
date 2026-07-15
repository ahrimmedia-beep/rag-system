import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.domain.embeddings import EmbeddingsProvider
from app.domain.models import Chunk
from app.domain.vector_store import VectorStore

_NAMESPACE = uuid.UUID("6f9619ff-8b86-d011-b42d-00cf4fc964ff")


class IngestionService:
    def __init__(
        self,
        embeddings: EmbeddingsProvider,
        store: VectorStore,
        embeddings_dim: int,
        chunk_size: int = 900,
        chunk_overlap: int = 50,
    ) -> None:
        self._embeddings = embeddings
        self._store = store
        self._embeddings_dim = embeddings_dim
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def ingest(self, text: str, metadata: dict[str, object]) -> int:
        """Additive/idempotent by (source, chunk_index); never deletes superseded chunks."""
        self._store.ensure_collection(self._embeddings_dim)
        pieces = [p for p in self._splitter.split_text(text) if p.strip()]
        if not pieces:
            return 0
        source = str(metadata.get("source", "unknown"))
        chunks = [
            Chunk(
                id=str(uuid.uuid5(_NAMESPACE, f"{source}:{i}")),
                text=piece,
                metadata={**metadata, "chunk_index": i},
            )
            for i, piece in enumerate(pieces)
        ]
        vectors = self._embeddings.embed_documents([c.text for c in chunks])
        self._store.upsert(chunks, vectors)
        return len(chunks)
