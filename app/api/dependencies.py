from functools import lru_cache

from app.adapters.embeddings_openai import OpenAIEmbeddings
from app.adapters.llm_openai import OpenAILLM
from app.adapters.vector_qdrant import QdrantVectorStore
from app.config import get_settings
from app.domain.vector_store import VectorStore
from app.services.generation import GenerationService
from app.services.ingestion import IngestionService
from app.services.memory import MemoryService
from app.services.rag_agent import RagAgentService
from app.services.retrieval import RetrievalService


@lru_cache
def _memory(window: int) -> MemoryService:
    return MemoryService(window=window)


@lru_cache
def _embeddings() -> OpenAIEmbeddings:
    """Built once per process and reused across requests (no per-request re-dialing).
    Cached independently of `_llm`/`_store` so e.g. `/health` only pays for what it uses."""
    settings = get_settings()
    return OpenAIEmbeddings(settings.llm_base_url, settings.llm_api_key, settings.embeddings_model)


@lru_cache
def _llm() -> OpenAILLM:
    settings = get_settings()
    return OpenAILLM(settings.llm_base_url, settings.llm_api_key, settings.llm_model)


@lru_cache
def _store() -> QdrantVectorStore:
    settings = get_settings()
    return QdrantVectorStore(settings.qdrant_url, settings.qdrant_collection)


def get_ingestion_service() -> IngestionService:
    settings = get_settings()
    return IngestionService(
        _embeddings(),
        _store(),
        settings.embeddings_dim,
        settings.chunk_size,
        settings.chunk_overlap,
    )


def get_rag_agent_service() -> RagAgentService:
    settings = get_settings()
    retrieval = RetrievalService(_embeddings(), _store(), settings.top_k, settings.score_threshold)
    generation = GenerationService(_llm())
    memory = _memory(settings.memory_window)
    return RagAgentService(_llm(), retrieval, generation, memory)


def get_vector_store() -> VectorStore:
    return _store()
