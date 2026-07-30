"""Integration test configuration.

Strategy:
- httpx.AsyncClient + ASGITransport — no real HTTP server needed
- get_session is overridden to use a dedicated test engine (localhost PostgreSQL)
- get_users_email_service is overridden with a MagicMock — no real SMTP
- Rate limiter is replaced with an in-memory instance per test to prevent interference
- All user tables are TRUNCATED after every test for full isolation

Environment:
- TEST_DATABASE_URL — explicit test DB URL (recommended).
  Falls back to DATABASE_URL with host substitution @postgres: → @localhost:
  for backwards compatibility with docker-compose setups.
"""
import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from core.database import get_session
from core.main import app
from core.settings import settings
from modules.notifications.dependencies import get_users_email_service
from modules.notifications.services.users_email import UsersEmailService

# ---------------------------------------------------------------------------
# Engine (session-scoped — created once for the entire integration suite)
# ---------------------------------------------------------------------------

INTEGRATION_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    settings.DATABASE_URL.replace("@postgres:", "@localhost:"),
)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def integration_engine():
    from core.models.base import Base
    from modules.users.models import AccessToken, LoginCode, User  # noqa: F401 — register models
    from modules.users.models.login_attempt import LoginAttempt  # noqa: F401

    # NullPool: no connection reuse between sessions — prevents asyncpg
    # "another operation is in progress" errors under concurrent fixture teardown.
    engine = create_async_engine(INTEGRATION_DB_URL, echo=False, poolclass=NullPool)
    async with engine.begin() as conn:
        # Ensure the users schema and all tables exist (Alembic may not have run in CI)
        await conn.execute(text("CREATE SCHEMA IF NOT EXISTS users"))
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def integration_session_factory(integration_engine):
    return async_sessionmaker(
        integration_engine, class_=AsyncSession, expire_on_commit=False
    )


# ---------------------------------------------------------------------------
# DB isolation — truncate all user tables after every test
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(integration_engine):
    yield
    async with integration_engine.begin() as conn:
        await conn.execute(text(
            "TRUNCATE TABLE "
            "users.login_attempt, users.access_token, "
            'users.login_code, users."user" '
            "RESTART IDENTITY CASCADE"
        ))


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_email_service() -> MagicMock:
    svc = MagicMock(spec=UsersEmailService)
    svc.send_login_code_email_task = MagicMock(return_value=None)
    svc.send_welcome_email_task = MagicMock(return_value=None)
    svc.send_login_code_email = AsyncMock(return_value=True)
    svc.send_welcome_email = AsyncMock(return_value=True)
    return svc


@pytest_asyncio.fixture
async def client(
    integration_session_factory, mock_email_service
) -> AsyncGenerator[AsyncClient]:
    """AsyncClient with all external dependencies overridden."""

    async def override_get_session():
        async with integration_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_get_email_service():
        return mock_email_service

    # Disable rate limiting in two places:
    # 1. app.state.limiter — used by SlowAPIMiddleware
    # 2. core.limiter.limiter — referenced directly by @limiter.limit() decorator wrappers
    import core.limiter as _core_limiter
    original_limiter = app.state.limiter
    original_enabled = _core_limiter.limiter.enabled
    app.state.limiter = Limiter(key_func=get_remote_address, enabled=False)
    _core_limiter.limiter.enabled = False
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_users_email_service] = override_get_email_service

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    app.state.limiter = original_limiter
    _core_limiter.limiter.enabled = original_enabled


# ---------------------------------------------------------------------------
# Direct DB session for test data setup
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def db_session(integration_session_factory) -> AsyncGenerator[AsyncSession]:
    """Session for inserting test data directly into the DB."""
    async with integration_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
