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