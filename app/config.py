from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    embeddings_model: str = "text-embedding-3-small"
    embeddings_dim: int = 1536

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "knowledge_base"

    chunk_size: int = 900
    chunk_overlap: int = 50
    top_k: int = 5
    memory_window: int = 20
    score_threshold: float = 0.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
