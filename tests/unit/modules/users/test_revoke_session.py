"""Unit tests for AuthMagicLinkService.revoke_session."""
import pytest

from modules.users.exceptions import AccessTokenNotFound
from modules.users.services.auth_service import AuthMagicLinkService


@pytest.mark.unit
class TestRevokeSession:
    async def test_revokes_own_session(
        self,
        auth_service: AuthMagicLinkService,
        mock_access_token_repo,
    ):
        mock_access_token_repo.deactivate_token_by_id.return_value = True

        await auth_service.revoke_session(user_id=1, token_id=42)

        mock_access_token_repo.deactivate_token_by_id.assert_awaited_once_with(1, 42)

    async def test_nonexistent_session_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_access_token_repo,
    ):
        mock_access_token_repo.deactivate_token_by_id.return_value = False

        with pytest.raises(AccessTokenNotFound):
            await auth_service.revoke_session(user_id=1, token_id=999)

    async def test_another_users_session_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_access_token_repo,
    ):
        """Repo returns False when user_id doesn't match — service must raise, not silently succeed."""
        mock_access_token_repo.deactivate_token_by_id.return_value = False

        with pytest.raises(AccessTokenNotFound):
            await auth_service.revoke_session(user_id=1, token_id=7)

    async def test_commits_on_success(
        self,
        auth_service: AuthMagicLinkService,
        mock_access_token_repo,
        mock_session,
    ):
        mock_access_token_repo.deactivate_token_by_id.return_value = True

        await auth_service.revoke_session(user_id=1, token_id=1)

        mock_session.commit.assert_awaited_once()
