"""Unit tests for AuthMagicLinkService.logout."""
import pytest

from modules.users.exceptions import AccessTokenNotFound
from modules.users.services.auth_service import AuthMagicLinkService


@pytest.mark.unit
class TestLogout:
    async def test_with_token_deactivates_it(
        self,
        auth_service: AuthMagicLinkService,
        mock_access_token_repo,
    ):
        mock_access_token_repo.deactivate_token.return_value = True

        await auth_service.logout(user_id=1, token="test-token-abc")

        mock_access_token_repo.deactivate_token.assert_awaited_once_with(1, "test-token-abc")

    async def test_without_token_deactivates_all(
        self,
        auth_service: AuthMagicLinkService,
        mock_access_token_repo,
    ):
        await auth_service.logout(user_id=1)

        mock_access_token_repo.deactivate_all_tokens.assert_awaited_once_with(1)

    async def test_nonexistent_token_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_access_token_repo,
    ):
        mock_access_token_repo.deactivate_token.return_value = False

        with pytest.raises(AccessTokenNotFound):
            await auth_service.logout(user_id=1, token="does-not-exist")
