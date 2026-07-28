"""Pytest configuration and fixtures."""
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import os

from core.settings import settings

from sqlalchemy import text

from core.models.base import Base
from modules.users.models import User, LoginCode, AccessToken, LoginAttempt  # noqa: F401

# ============================================================================
# Database
# ============================================================================

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_engine():
    """Create test database engine once per session."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS users"))
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS admin"))
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def db_setup(test_engine):
    """Ensure DB schema and tables are created before any test."""
    yield


@pytest_asyncio.fixture
async def test_session(db_setup) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.connect() as conn:
        await conn.begin_nested()
        async_session = async_sessionmaker(
            bind=conn,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with async_session() as session:
            yield session
            await session.rollback()
    await engine.dispose()
# ============================================================================
# Settings
# ============================================================================

@pytest.fixture
def test_settings(monkeypatch):
    """Override settings for tests."""
    monkeypatch.setattr(settings, "DEBUG", True)
    return settings


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
