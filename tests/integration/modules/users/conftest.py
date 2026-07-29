"""Fixtures for users integration tests."""
import datetime
import secrets
from collections.abc import Callable, Awaitable

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.settings import users_settings
from modules.users.models import AccessToken, LoginCode, User


@pytest_asyncio.fixture
async def existing_user(db_session: AsyncSession) -> User:
    """A regular active user pre-seeded in the DB."""
    user = User(
        email="testuser@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def inactive_user(db_session: AsyncSession) -> User:
    user = User(
        email="inactive@example.com",
        hashed_password="hashed_password",
        is_active=False,
        is_superuser=False,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_token(existing_user: User, db_session: AsyncSession) -> str:
    """A valid access token for existing_user."""
    token_value = secrets.token_urlsafe(48)
    token = AccessToken(
        token=token_value,
        user_id=existing_user.id,
        is_active=True,
        expires_at=datetime.datetime.now(datetime.UTC) + users_settings.ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
    )
    db_session.add(token)
    await db_session.commit()
    return token_value


@pytest_asyncio.fixture
async def auth_headers(user_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {user_token}"}


@pytest_asyncio.fixture
def seed_user_with_code(
    db_session: AsyncSession,
) -> Callable[..., Awaitable[User]]:
    """Factory fixture: creates an active user with a valid login code."""
    async def _factory(
        email: str = "verify@example.com",
        code: str = "123456",
    ) -> User:
        user = User(
            email=email,
            hashed_password="hashed",
            is_active=True,
            is_verified=True,
        )
        db_session.add(user)
        await db_session.flush()

        db_session.add(LoginCode(
            code=code,
            user_id=user.id,
            is_active=True,
            expires_at=datetime.datetime.now(datetime.UTC) + users_settings.LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        ))
        await db_session.commit()
        return user

    return _factory


@pytest_asyncio.fixture
async def user_with_expired_code(db_session: AsyncSession) -> User:
    """An active user whose login code has already expired."""
    user = User(
        email="expired@example.com",
        hashed_password="x",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.flush()

    db_session.add(LoginCode(
        code="333333",
        user_id=user.id,
        is_active=True,
        expires_at=datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1),
    ))
    await db_session.commit()
    return user
