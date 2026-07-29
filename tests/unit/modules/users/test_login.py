"""Unit tests for AuthMagicLinkService.login."""
import pytest
from fastapi_users import exceptions as fu_exc

from modules.users.exceptions import AuthErrorException
from modules.users.services.auth_service import AuthMagicLinkService


EMAIL = "test@example.com"


@pytest.mark.unit
class TestLogin:
    async def test_creates_new_user_when_not_exists(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        make_user,
        make_login_code,
    ):
        mock_user_manager.get_by_email.side_effect = fu_exc.UserNotExists()
        new_user = make_user(email=EMAIL)
        mock_user_manager.create.return_value = new_user
        mock_login_code_repo.create.return_value = make_login_code()

        user = await auth_service.login(EMAIL)

        mock_user_manager.create.assert_awaited_once()
        assert user.email == EMAIL

    async def test_returns_existing_user(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        make_user,
        make_login_code,
    ):
        existing = make_user(id=5, email=EMAIL)
        mock_user_manager.get_by_email.return_value = existing
        mock_login_code_repo.create.return_value = make_login_code()

        user = await auth_service.login(EMAIL)

        assert user.id == 5

    async def test_sends_email_with_code(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_email_service,
        make_user,
        make_login_code,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_code_repo.create.return_value = make_login_code()

        await auth_service.login(EMAIL)

        mock_email_service.send_login_code_email_task.assert_called_once()

    async def test_email_contains_six_digit_code(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_email_service,
        make_user,
        make_login_code,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_code_repo.create.return_value = make_login_code()

        await auth_service.login(EMAIL)

        code = mock_email_service.send_login_code_email_task.call_args[0][1]
        assert len(code) == 6
        assert code.isdigit()

    async def test_inactive_user_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        make_user,
    ):
        mock_user_manager.get_by_email.return_value = make_user(is_active=False)

        with pytest.raises(AuthErrorException):
            await auth_service.login(EMAIL)

    async def test_deactivates_previous_codes_before_creating_new(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        make_user,
        make_login_code,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_code_repo.create.return_value = make_login_code()

        await auth_service.login(EMAIL)

        mock_login_code_repo.deactivate_all_for_user.assert_awaited_once()
