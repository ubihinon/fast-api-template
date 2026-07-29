"""Shared fixtures for users unit tests."""
import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from modules.notifications.services.users_email import UsersEmailService
from modules.users.manager import UserManager
from modules.users.models import AccessToken, LoginCode, User
from modules.users.repositories import AccessTokenRepository
from modules.users.repositories.login_attempt import LoginAttemptRepository
from modules.users.repositories.login_code import LoginCodeRepository
from modules.users.repositories.user import UserRepository
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import users_settings


# ---------------------------------------------------------------------------
# Builder helpers — callable fixtures so tests can create objects with custom args
# ---------------------------------------------------------------------------

@pytest.fixture
def make_user():
    def _make(
        id: int = 1,
        email: str = "test@example.com",
        is_active: bool = True,
    ) -> MagicMock:
        user = MagicMock(spec=User)
        user.id = id
        user.email = email
        user.is_active = is_active
        return user

    return _make


@pytest.fixture
def make_login_code():
    def _make(
        id: int = 1,
        code: str = "123456",
        user_id: int = 1,
        is_active: bool = True,
    ) -> MagicMock:
        lc = MagicMock(spec=LoginCode)
        lc.id = id
        lc.code = code
        lc.user_id = user_id
        lc.is_active = is_active
        return lc

    return _make


@pytest.fixture
def make_access_token():
    def _make(
        id: int = 1,
        token: str = "test-access-token",
        user_id: int = 1,
        is_active: bool = True,
    ) -> MagicMock:
        at = MagicMock(spec=AccessToken)
        at.id = id
        at.token = token
        at.user_id = user_id
        at.is_active = is_active
        at.created_at = datetime.datetime.now(datetime.UTC)
        at.expires_at = (
            datetime.datetime.now(datetime.UTC) + users_settings.ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA
        )
        return at

    return _make


# ---------------------------------------------------------------------------
# Mocked dependencies
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_user_manager():
    return AsyncMock(spec=UserManager)


@pytest.fixture
def mock_user_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_login_code_repo():
    return AsyncMock(spec=LoginCodeRepository)


@pytest.fixture
def mock_login_attempt_repo():
    repo = AsyncMock(spec=LoginAttemptRepository)
    repo.get_failed_attempts_count.return_value = 0
    return repo


@pytest.fixture
def mock_access_token_repo():
    return AsyncMock(spec=AccessTokenRepository)


@pytest.fixture
def mock_email_service():
    svc = MagicMock(spec=UsersEmailService)
    svc.send_login_code_email_task = MagicMock(return_value=None)
    return svc


# ---------------------------------------------------------------------------
# Service under test — wired with all mocked dependencies
# ---------------------------------------------------------------------------

@pytest.fixture
def auth_service(
    mock_session,
    mock_user_repo,
    mock_login_code_repo,
    mock_login_attempt_repo,
    mock_access_token_repo,
    mock_email_service,
    mock_user_manager,
) -> AuthMagicLinkService:
    return AuthMagicLinkService(
        session=mock_session,
        user_repository=mock_user_repo,
        login_code_repository=mock_login_code_repo,
        login_attempt_repository=mock_login_attempt_repo,
        access_token_repository=mock_access_token_repo,
        email_service=mock_email_service,
        user_manager=mock_user_manager,
        ip_address="127.0.0.1",
        user_agent="Mozilla/5.0 (test)",
    )
