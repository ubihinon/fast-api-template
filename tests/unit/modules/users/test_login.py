"""Unit tests for AuthMagicLinkService.login."""
import pytest

from modules.users.exceptions import AuthErrorException
from modules.users.services.auth_service import AuthMagicLinkService


@pytest.mark.unit
@pytest.mark.asyncio
class TestLogin:
    async def test_creates_new_user_when_not_exists(
        self, auth_service: AuthMagicLinkService
    ):
        user = await auth_service.login("newuser@example.com")

        assert user.email == "newuser@example.com"
        assert user.is_active is True

    async def test_returns_existing_user(
        self, auth_service: AuthMagicLinkService, test_session, user_factory
    ):
        existing = await user_factory(test_session, email="existing@example.com")

        user = await auth_service.login(existing.email)

        assert user.id == existing.id

    async def test_sends_email_with_code(
        self, auth_service: AuthMagicLinkService, test_session, user_factory
    ):
        await user_factory(test_session, email="user@example.com")

        await auth_service.login("user@example.com")

        auth_service.email_service.send_login_code_email_task.assert_called_once()

    async def test_email_contains_six_digit_code(
        self, auth_service: AuthMagicLinkService, test_session, user_factory
    ):
        await user_factory(test_session, email="codecheck@example.com")

        await auth_service.login("codecheck@example.com")

        code = auth_service.email_service.send_login_code_email_task.call_args[0][1]
        assert len(code) == 6
        assert code.isdigit()

    async def test_inactive_user_raises(
        self, auth_service: AuthMagicLinkService, test_session, user_factory
    ):
        await user_factory(test_session, email="inactive@example.com", is_active=False)

        with pytest.raises(AuthErrorException):
            await auth_service.login("inactive@example.com")
