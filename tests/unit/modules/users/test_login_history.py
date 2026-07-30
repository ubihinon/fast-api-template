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
    async def test_returns_items_for_user(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        mock_login_attempt_repo.get_history.return_value = [
            _make_attempt(id=2), _make_attempt(id=1),
        ]

        result = await auth_service.get_login_history(user_id=1)

        mock_login_attempt_repo.get_history.assert_awaited_once_with(1, limit=50, cursor=None)
        assert len(result.items) == 2

    async def test_passes_limit_and_cursor(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        mock_login_attempt_repo.get_history.return_value = []

        await auth_service.get_login_history(user_id=1, limit=10, cursor=42)

        mock_login_attempt_repo.get_history.assert_awaited_once_with(1, limit=10, cursor=42)

    async def test_next_cursor_set_when_full_page(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        """When returned items == limit, next_cursor is the last item's id."""
        attempts = [_make_attempt(id=10 - i) for i in range(3)]  # ids: 10, 9, 8
        mock_login_attempt_repo.get_history.return_value = attempts

        result = await auth_service.get_login_history(user_id=1, limit=3)

        assert result.next_cursor == 8  # last item's id

    async def test_next_cursor_none_when_partial_page(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        """When returned items < limit, it's the last page — next_cursor is None."""
        mock_login_attempt_repo.get_history.return_value = [_make_attempt(id=5)]

        result = await auth_service.get_login_history(user_id=1, limit=50)

        assert result.next_cursor is None

    async def test_empty_history(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        mock_login_attempt_repo.get_history.return_value = []

        result = await auth_service.get_login_history(user_id=1)

        assert result.items == []
        assert result.next_cursor is None

    async def test_code_entered_not_in_schema(
        self,
        auth_service: AuthMagicLinkService,
        mock_login_attempt_repo,
    ):
        """code_entered and email must never be exposed through LoginAttemptSchema."""
        mock_login_attempt_repo.get_history.return_value = [_make_attempt()]

        result = await auth_service.get_login_history(user_id=1)

        assert not hasattr(result.items[0], "code_entered")
        assert not hasattr(result.items[0], "email")
