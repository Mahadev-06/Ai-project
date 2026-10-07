"""Pytest configuration and fixtures for ClaimLens tests."""
import asyncio
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.database import init_db, engine, Base
from app.config import get_settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_client():
    """Provides an AsyncClient bound to the FastAPI app."""
    # Ensure test database initialized
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
