"""Unit tests for AuthMagicLinkService.verify_login_code."""
import datetime

import pytest

from modules.users.exceptions import (
    LoginCodeInvalidException,
    LoginMaxNumberAttemptsException,
    UserNotFoundException,
)
from modules.users.models import LoginCode
from modules.users.repositories import LoginCodeRepository
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA, MAX_LOGIN_ATTEMPTS


@pytest.mark.unit
@pytest.mark.asyncio
class TestVerifyLoginCode:
    async def test_valid_code_returns_active_token(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        login_code = await login_code_factory(test_session, user.id)

        token = await auth_service.verify_login_code(user.email, login_code.code)

        assert token.token is not None
        assert token.is_active is True

    async def test_valid_code_token_expires_in_one_hour(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        login_code = await login_code_factory(test_session, user.id)

        token = await auth_service.verify_login_code(user.email, login_code.code)

        expected = (
            datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA
        ).replace(minute=0, second=0, microsecond=0)
        actual = token.expires_at.replace(minute=0, second=0, microsecond=0)
        assert actual == expected

    async def test_nonexistent_email_raises(self, auth_service: AuthMagicLinkService):
        with pytest.raises(UserNotFoundException):
            await auth_service.verify_login_code("ghost@example.com", "123456")

    async def test_wrong_code_raises(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="111111")

        with pytest.raises(LoginCodeInvalidException):
            await auth_service.verify_login_code(user.email, "999999")

    async def test_inactive_code_raises(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="222222", is_active=False)

        with pytest.raises(LoginCodeInvalidException):
            await auth_service.verify_login_code(user.email, "222222")

    async def test_expired_code_raises(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
    ):
        user = await user_factory(test_session)
        test_session.add(LoginCode(
            code="333333",
            user_id=user.id,
            is_active=True,
            expires_at=datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1),
        ))
        await test_session.commit()

        with pytest.raises(LoginCodeInvalidException):
            await auth_service.verify_login_code(user.email, "333333")

    async def test_code_deactivated_after_use(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="444444")

        await auth_service.verify_login_code(user.email, "444444")

        active = await LoginCodeRepository(test_session).get_active("444444", user.id)
        assert active is None

    async def test_max_attempts_exceeded_raises(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="555555")

        for _ in range(MAX_LOGIN_ATTEMPTS):
            with pytest.raises(LoginCodeInvalidException):
                await auth_service.verify_login_code(user.email, "000000")

        with pytest.raises(LoginMaxNumberAttemptsException):
            await auth_service.verify_login_code(user.email, "000000")

    async def test_one_failure_does_not_block_correct_code(
        self,
        auth_service: AuthMagicLinkService,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="666666")

        with pytest.raises(LoginCodeInvalidException):
            await auth_service.verify_login_code(user.email, "000000")

        token = await auth_service.verify_login_code(user.email, "666666")
        assert token.is_active is True
