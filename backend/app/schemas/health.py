"""Health and readiness schemas."""
from typing import Dict, Any, Optional
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"


class CorpusStatus(BaseModel):
    loaded: bool
    version: str
    passages: int


class ProviderStatus(BaseModel):
    brave_configured: bool
    google_factcheck_configured: bool


class ReadinessResponse(BaseModel):
    ready: bool
    models: Dict[str, str]
    corpus: CorpusStatus
    providers: ProviderStatus
