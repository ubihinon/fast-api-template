"""Shared fixtures for users unit tests."""
import datetime
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.manager import UserManager
from modules.users.models import LoginCode, User
from modules.users.repositories import (
    AccessTokenRepository,
    LoginAttemptRepository,
    LoginCodeRepository,
    UserRepository,
)
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import LOGIN_CODE_EXPIRES_IN_TIMEDELTA


def make_service(session: AsyncSession, ip_address: str = "127.0.0.1") -> AuthMagicLinkService:
    email_service = MagicMock()
    email_service.send_login_code_email_task = MagicMock(return_value=None)
    user_manager = UserManager(User.get_db(session), email_service)
    return AuthMagicLinkService(
        session=session,
        user_repository=UserRepository(session),
        login_code_repository=LoginCodeRepository(session),
        login_attempt_repository=LoginAttemptRepository(session),
        access_token_repository=AccessTokenRepository(session),
        email_service=email_service,
        user_manager=user_manager,
        ip_address=ip_address,
    )


@pytest.fixture
def auth_service(test_session: AsyncSession) -> AuthMagicLinkService:
    return make_service(test_session)


@pytest_asyncio.fixture
async def user_factory():
    async def _create_user(
        session: AsyncSession,
        email: str = "test@example.com",
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email,
            hashed_password="password123",
            is_active=is_active,
            is_superuser=is_superuser,
        )
        session.add(user)
        await session.flush()
        await session.refresh(user)
        return user

    return _create_user


@pytest_asyncio.fixture
async def login_code_factory():
    """Factory for creating test login codes."""

    async def _create_login_code(
        session: AsyncSession,
        user_id: UserIdType,
        code: str = "123456",
        is_active: bool = True,
    ) -> LoginCode:
        login_code = LoginCode(
            code=code,
            user_id=user_id,
            is_active=is_active,
            expires_at=datetime.datetime.now(datetime.UTC) + LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        )
        session.add(login_code)
        await session.flush()
        await session.refresh(login_code)
        return login_code

    return _create_login_code
