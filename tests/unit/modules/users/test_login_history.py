"""Unit tests for AuthMagicLinkService.get_login_history."""
import datetime
from unittest.mock import MagicMock

import pytest

from modules.users.models import LoginAttempt
from modules.users.services.auth_service import AuthMagicLinkService


def _make_attempt(
    id: int = 1,
    is_correct: bool = True,
    ip_address: str | None = "127.0.0.1",
    user_agent: str | None = "Mozilla/5.0",
) -> MagicMock:
    a = MagicMock(spec=LoginAttempt)
    a.id = id
    a.created_at = datetime.datetime.now(datetime.UTC)
    a.is_correct = is_correct
    a.ip_address = ip_address
    a.user_agent = user_agent
    return a


@pytest.mark.unit
class TestGetLoginHistory:
    async def test_returns_attempts_for_user(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        attempts = [_make_attempt(id=1, is_correct=True), _make_attempt(id=2, is_correct=False)]
        mock_login_attempt_repo.get_history.return_value = attempts

        result = await auth_service.get_login_history(user_id=1)

        mock_login_attempt_repo.get_history.assert_awaited_once_with(1, limit=50, offset=0)
        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 2

    async def test_passes_limit_and_offset(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        mock_login_attempt_repo.get_history.return_value = []

        await auth_service.get_login_history(user_id=1, limit=10, offset=20)

        mock_login_attempt_repo.get_history.assert_awaited_once_with(1, limit=10, offset=20)

    async def test_empty_history_returns_empty_list(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        mock_login_attempt_repo.get_history.return_value = []

        result = await auth_service.get_login_history(user_id=1)

        assert result == []

    async def test_code_entered_not_in_schema(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        """code_entered must never be exposed through LoginAttemptSchema."""
        mock_login_attempt_repo.get_history.return_value = [_make_attempt()]

        result = await auth_service.get_login_history(user_id=1)

        assert not hasattr(result[0], "code_entered")
        assert not hasattr(result[0], "email")
