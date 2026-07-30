"""Unit tests for AuthMagicLinkService.verify_login_code."""
import datetime

import pytest
from fastapi_users import exceptions as fu_exc

from modules.users.exceptions import (
    LoginCodeInvalidException,
    LoginMaxNumberAttemptsException,
    UserNotFoundException,
)
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import users_settings

EMAIL = "test@example.com"


@pytest.mark.unit
class TestVerifyLoginCode:
    async def test_valid_code_returns_active_token(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_login_attempt_repo,
        mock_access_token_repo,
        make_user,
        make_login_code,
        make_access_token,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_attempt_repo.get_failed_attempts_count.return_value = 0
        mock_login_code_repo.get_active_and_deactivate.return_value = make_login_code()
        mock_access_token_repo.create.return_value = make_access_token()

        token = await auth_service.verify_login_code(EMAIL, "123456")

        assert token.token is not None
        assert token.is_active is True

    async def test_valid_code_token_expires_in_one_hour(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_login_attempt_repo,
        mock_access_token_repo,
        make_user,
        make_login_code,
        make_access_token,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_attempt_repo.get_failed_attempts_count.return_value = 0
        mock_login_code_repo.get_active_and_deactivate.return_value = make_login_code()
        mock_access_token_repo.create.return_value = make_access_token()

        before = datetime.datetime.now(datetime.UTC)
        await auth_service.verify_login_code(EMAIL, "123456")
        after = datetime.datetime.now(datetime.UTC)

        _, kwargs = mock_access_token_repo.create.call_args
        expires_at = kwargs["expires_at"]
        expected_min = before + users_settings.ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA
        expected_max = after + users_settings.ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA
        assert expected_min <= expires_at <= expected_max

    async def test_nonexistent_email_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
    ):
        mock_user_manager.get_by_email.side_effect = fu_exc.UserNotExists()

        with pytest.raises(UserNotFoundException):
            await auth_service.verify_login_code("ghost@example.com", "123456")

    async def test_wrong_code_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_login_attempt_repo,
        make_user,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_attempt_repo.get_failed_attempts_count.return_value = 0
        mock_login_code_repo.get_active_and_deactivate.return_value = None

        with pytest.raises(LoginCodeInvalidException):
            await auth_service.verify_login_code(EMAIL, "999999")

    @pytest.mark.parametrize("code", ["222222", "333333"], ids=["inactive", "expired"])
    async def test_inactive_or_expired_code_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_login_attempt_repo,
        make_user,
        code: str,
    ):
        # The repository filters out both inactive and expired codes by returning None.
        # Both cases are indistinguishable at the service layer.
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_attempt_repo.get_failed_attempts_count.return_value = 0
        mock_login_code_repo.get_active_and_deactivate.return_value = None

        with pytest.raises(LoginCodeInvalidException):
            await auth_service.verify_login_code(EMAIL, code)

    async def test_code_deactivated_after_use(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_login_attempt_repo,
        mock_access_token_repo,
        make_user,
        make_login_code,
        make_access_token,
    ):
        login_code = make_login_code(id=42, code="444444")
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_attempt_repo.get_failed_attempts_count.return_value = 0
        mock_login_code_repo.get_active_and_deactivate.return_value = login_code
        mock_access_token_repo.create.return_value = make_access_token()

        await auth_service.verify_login_code(EMAIL, "444444")

        mock_login_code_repo.get_active_and_deactivate.assert_awaited_once_with("444444", make_user().id)

    async def test_max_attempts_exceeded_raises(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_attempt_repo,
        make_user,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_attempt_repo.get_failed_attempts_count.return_value = users_settings.MAX_LOGIN_ATTEMPTS

        with pytest.raises(LoginMaxNumberAttemptsException):
            await auth_service.verify_login_code(EMAIL, "000000")

    async def test_one_failure_does_not_block_correct_code(
        self,
        auth_service: AuthMagicLinkService,
        mock_user_manager,
        mock_login_code_repo,
        mock_login_attempt_repo,
        mock_access_token_repo,
        make_user,
        make_login_code,
        make_access_token,
    ):
        mock_user_manager.get_by_email.return_value = make_user()
        mock_login_attempt_repo.get_failed_attempts_count.side_effect = [0, 1]
        mock_login_code_repo.get_active_and_deactivate.side_effect = [None, make_login_code(code="666666")]
        mock_access_token_repo.create.return_value = make_access_token()

        with pytest.raises(LoginCodeInvalidException):
            await auth_service.verify_login_code(EMAIL, "000000")

        token = await auth_service.verify_login_code(EMAIL, "666666")
        assert token.is_active is True
