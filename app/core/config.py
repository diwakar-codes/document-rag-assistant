from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application
    APP_NAME: str
    APP_VERSION: str
    API_PREFIX: str

    # Groq
    GROQ_API_KEY: str

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_INDEX: str

    # Embeddings
    EMBEDDING_MODEL: str
    # Rag configs
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    DEFAULT_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.10

    # Hybrid retrieval (dense + BM25)
    HYBRID_ALPHA: float = 0.5
    BM25_CANDIDATE_POOL: int = 30

    # Groq generation
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    DEFAULT_TEMPERATURE: float = 0.2
    DEFAULT_MAX_TOKENS: int = 1024

    # Vision OCR
    GROQ_VISION_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    OCR_MIN_CHARS_PER_PAGE: int = 20

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()