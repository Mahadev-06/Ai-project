"""Application configuration from environment variables."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration loaded from environment / .env file."""

    # API Keys (optional - only for live mode)
    BRAVE_API_KEY: Optional[str] = None
    GOOGLE_FACTCHECK_API_KEY: Optional[str] = None

    # Database
    DATABASE_URL: str = 'sqlite+aiosqlite:///./claimlens.db'

    # Corpus and models
    CORPUS_DIR: str = 'data/corpus'
    MODEL_CACHE_DIR: str = '.model_cache'

    # Processing limits
    MAX_INPUT_CHARS: int = 10000
    MAX_CLAIMS_PER_ANALYSIS: int = 6
    MAX_EVIDENCE_PER_CLAIM: int = 5
    MAX_SEARCH_QUERIES_PER_CLAIM: int = 2
    MAX_FETCHED_PAGES: int = 10

    # Job management
    JOB_TIMEOUT_SECONDS: int = 300
    JOB_RETENTION_HOURS: int = 24
    MAX_QUEUE_SIZE: int = 10

    # CORS
    ALLOWED_ORIGINS: list[str] = ['http://localhost:5173', 'http://localhost:3000']

    # Models
    EMBEDDING_MODEL: str = 'sentence-transformers/all-MiniLM-L6-v2'
    NLI_MODEL: str = 'cross-encoder/nli-deberta-v3-small'
    SPACY_MODEL: str = 'en_core_web_sm'

    # Decision policy thresholds (provisional)
    ENTAILMENT_THRESHOLD: float = 0.65
    CONTRADICTION_THRESHOLD: float = 0.65
    MIN_RELEVANCE_SCORE: float = 0.25

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias
settings = get_settings()
