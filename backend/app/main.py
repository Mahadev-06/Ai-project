"""ClaimLens FastAPI application entry point."""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.router import api_router
from app.models.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize DB and load models."""
    settings = get_settings()

    # Initialize database
    await init_db()
    logger.info('Database initialized')

    # Load ML models in background task so server binds immediately
    from app.services.model_manager import model_manager
    loop = asyncio.get_event_loop()

    async def _load_models_bg():
        try:
            await loop.run_in_executor(
                None,
                lambda: model_manager.load_all(
                    embedding_model=settings.EMBEDDING_MODEL,
                    nli_model=settings.NLI_MODEL,
                    spacy_model=settings.SPACY_MODEL,
                )
            )
            if model_manager.is_ready:
                logger.info('All models loaded and ready')
            else:
                logger.warning(f'Some models failed to load: {model_manager.load_errors}')
        except Exception as e:
            logger.error(f'Model loading failed: {e}')

    asyncio.create_task(_load_models_bg())

    yield

    logger.info('Application shutting down')


app = FastAPI(
    title='ClaimLens API',
    description='AI-Based Misinformation Detection System',
    version='0.1.0',
    lifespan=lifespan,
)

# CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=r'https?://.*',
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Include API routes
app.include_router(api_router, prefix='/api/v1')


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Return structured error without exposing internals."""
    logger.error(f'Unhandled error: {exc}', exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': 'An internal error occurred. Please try again.'},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': str(exc)},
    )