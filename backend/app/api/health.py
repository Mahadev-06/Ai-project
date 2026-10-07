"""Health and system readiness endpoints."""
from fastapi import APIRouter
from app.config import get_settings
from app.schemas.health import HealthResponse, ReadinessResponse, CorpusStatus, ProviderStatus
from app.services.model_manager import model_manager
from app.services.retrieval.corpus import CorpusLoader

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def health_check():
    """Liveness probe: returns 200 if server is listening."""
    return HealthResponse(status="ok", version="0.1.0")


@router.get("/readiness", response_model=ReadinessResponse)
async def readiness_check():
    """Readiness probe: inspects model weights, local corpus, and external provider configs."""
    settings = get_settings()

    # Check corpus
    corpus = CorpusLoader(settings.CORPUS_DIR)
    corpus.load()

    # Check providers
    brave_ok = bool(settings.BRAVE_API_KEY and settings.BRAVE_API_KEY.strip())
    factcheck_ok = bool(settings.GOOGLE_FACTCHECK_API_KEY and settings.GOOGLE_FACTCHECK_API_KEY.strip())

    return ReadinessResponse(
        ready=model_manager.is_ready and corpus.is_loaded,
        models=model_manager.model_versions,
        corpus=CorpusStatus(
            loaded=corpus.is_loaded,
            version=corpus.version,
            passages=len(corpus.passages),
        ),
        providers=ProviderStatus(
            brave_configured=brave_ok,
            google_factcheck_configured=factcheck_ok,
        ),
    )