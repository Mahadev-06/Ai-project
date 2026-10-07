from fastapi import APIRouter
from . import health, analyses

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["analyses"])