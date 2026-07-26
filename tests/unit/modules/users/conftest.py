"""Shared fixtures for users unit tests."""
from unittest.mock import MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.repositories import (
    AccessTokenRepository,
    LoginAttemptRepository,
    LoginCodeRepository,
    UserRepository,
)
from modules.users.services.auth_service import AuthMagicLinkService


def make_service(session: AsyncSession, ip_address: str = "127.0.0.1") -> AuthMagicLinkService:
    email_service = MagicMock()
    email_service.send_login_code_email_task = MagicMock(return_value=None)
    return AuthMagicLinkService(
        session=session,
        user_repository=UserRepository(session),
        login_code_repository=LoginCodeRepository(session),
        login_attempt_repository=LoginAttemptRepository(session),
        access_token_repository=AccessTokenRepository(session),
        email_service=email_service,
        ip_address=ip_address,
    )


@pytest.fixture
def auth_service(test_session: AsyncSession) -> AuthMagicLinkService:
    return make_service(test_session)
