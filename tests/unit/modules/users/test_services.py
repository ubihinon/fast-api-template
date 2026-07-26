"""Unit tests for users module services."""
import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from modules.users.exceptions import (
    AccessTokenNotFound,
    AuthErrorException,
    LoginCodeInvalidException,
    LoginMaxNumberAttemptsException,
    UserNotFoundException,
)
from modules.users.models import AccessToken, LoginCode, User
from modules.users.repositories import (
    AccessTokenRepository,
    LoginAttemptRepository,
    LoginCodeRepository,
    UserRepository,
)
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA, MAX_LOGIN_ATTEMPTS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_service(test_session: AsyncSession) -> AuthMagicLinkService:
    """Build an AuthMagicLinkService with a mocked email service."""
    email_service = MagicMock()
    email_service.send_login_code_email_task = MagicMock(return_value=None)
    return AuthMagicLinkService(
        session=test_session,
        user_repository=UserRepository(test_session),
        login_code_repository=LoginCodeRepository(test_session),
        login_attempt_repository=LoginAttemptRepository(test_session),
        access_token_repository=AccessTokenRepository(test_session),
        email_service=email_service,
        ip_address="127.0.0.1",
    )


# ---------------------------------------------------------------------------
# Tests – generate_code
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGenerateCode:
    def test_code_is_six_digits(self):
        service = MagicMock(spec=AuthMagicLinkService)
        service.generate_code = AuthMagicLinkService.generate_code.__get__(service)
        code = service.generate_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_code_is_zero_padded(self):
        """generate_code must always return exactly 6 characters."""
        service = MagicMock(spec=AuthMagicLinkService)
        service.generate_code = AuthMagicLinkService.generate_code.__get__(service)
        # Run many times to increase chance of low numbers appearing
        for _ in range(50):
            code = service.generate_code()
            assert len(code) == 6


# ---------------------------------------------------------------------------
# Tests – login
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
class TestLoginService:
    async def test_login_creates_new_user_when_not_exists(
        self, test_session, user_factory
    ):
        service = make_service(test_session)
        new_email = "newuser@example.com"

        user = await service.login(new_email)

        assert user.email == new_email
        assert user.is_active is True

    async def test_login_returns_existing_user(self, test_session, user_factory):
        existing_user = await user_factory(test_session, email="existing@example.com")
        service = make_service(test_session)

        user = await service.login(existing_user.email)

        assert user.id == existing_user.id

    async def test_login_sends_email(self, test_session, user_factory):
        await user_factory(test_session, email="user@example.com")
        service = make_service(test_session)

        await service.login("user@example.com")

        service.email_service.send_login_code_email_task.assert_called_once()

    async def test_login_inactive_user_raises(self, test_session, user_factory):
        await user_factory(test_session, email="inactive@example.com", is_active=False)
        service = make_service(test_session)

        with pytest.raises(AuthErrorException):
            await service.login("inactive@example.com")

    async def test_login_creates_login_code(self, test_session, user_factory):
        await user_factory(test_session, email="codecheck@example.com")
        service = make_service(test_session)

        await service.login("codecheck@example.com")

        # email_service should have received the 6-digit code
        call_args = service.email_service.send_login_code_email_task.call_args
        code_arg = call_args[0][1]  # positional arg: email, code, timedelta
        assert len(code_arg) == 6
        assert code_arg.isdigit()


# ---------------------------------------------------------------------------
# Tests – verify_login_code
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
class TestVerifyLoginCodeService:
    async def test_verify_valid_login_code(
        self, test_session, user_factory, login_code_factory
    ):
        user = await user_factory(test_session)
        login_code = await login_code_factory(test_session, user.id)
        service = make_service(test_session)

        access_token = await service.verify_login_code(user.email, login_code.code)

        assert access_token.token is not None
        assert access_token.is_active is True

        expected_expires_at = (
            datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA
        ).replace(minute=0, second=0, microsecond=0)
        actual_expires_at = access_token.expires_at.replace(
            minute=0, second=0, microsecond=0
        )
        assert actual_expires_at == expected_expires_at

    async def test_verify_nonexistent_email_raises(
        self, test_session, login_code_factory
    ):
        service = make_service(test_session)

        with pytest.raises(UserNotFoundException):
            await service.verify_login_code("ghost@example.com", "123456")

    async def test_verify_wrong_code_raises(self, test_session, user_factory, login_code_factory):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="111111")
        service = make_service(test_session)

        with pytest.raises(LoginCodeInvalidException):
            await service.verify_login_code(user.email, "999999")

    async def test_verify_inactive_code_raises(
        self, test_session, user_factory, login_code_factory
    ):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="222222", is_active=False)
        service = make_service(test_session)

        with pytest.raises(LoginCodeInvalidException):
            await service.verify_login_code(user.email, "222222")

    async def test_verify_expired_code_raises(self, test_session, user_factory):
        user = await user_factory(test_session)

        expired_code = LoginCode(
            code="333333",
            user_id=user.id,
            is_active=True,
            expires_at=datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1),
        )
        test_session.add(expired_code)
        await test_session.commit()

        service = make_service(test_session)

        with pytest.raises(LoginCodeInvalidException):
            await service.verify_login_code(user.email, "333333")

    async def test_verify_deactivates_code_after_use(
        self, test_session, user_factory, login_code_factory
    ):
        user = await user_factory(test_session)
        login_code = await login_code_factory(test_session, user.id, code="444444")
        service = make_service(test_session)

        await service.verify_login_code(user.email, "444444")

        repo = LoginCodeRepository(test_session)
        active = await repo.get_active("444444", user.id)
        assert active is None

    async def test_verify_max_attempts_exceeded_raises(
        self, test_session, user_factory, login_code_factory
    ):
        user = await user_factory(test_session)
        await login_code_factory(test_session, user.id, code="555555")
        service = make_service(test_session)

        # Exhaust MAX_LOGIN_ATTEMPTS with a wrong code first
        for _ in range(MAX_LOGIN_ATTEMPTS):
            with pytest.raises(LoginCodeInvalidException):
                await service.verify_login_code(user.email, "000000")

        with pytest.raises(LoginMaxNumberAttemptsException):
            await service.verify_login_code(user.email, "000000")

    async def test_verify_second_attempt_with_correct_code_after_one_failure(
        self, test_session, user_factory, login_code_factory
    ):
        """One wrong attempt should not block a subsequent correct attempt."""
        user = await user_factory(test_session)
        login_code = await login_code_factory(test_session, user.id, code="666666")
        service = make_service(test_session)

        with pytest.raises(LoginCodeInvalidException):
            await service.verify_login_code(user.email, "000000")

        token = await service.verify_login_code(user.email, "666666")
        assert token.is_active is True


# ---------------------------------------------------------------------------
# Tests – logout
# ---------------------------------------------------------------------------

@pytest.mark.unit
@pytest.mark.asyncio
class TestLogoutService:
    async def _create_token(
        self, test_session: AsyncSession, user: User
    ) -> AccessToken:
        repo = AccessTokenRepository(test_session)
        token = await repo.create(
            token="test-token-abc",
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
        )
        await test_session.commit()
        return token

    async def test_logout_with_specific_token_deactivates_it(
        self, test_session, user_factory
    ):
        from sqlalchemy import select as sa_select
        from modules.users.models import AccessToken

        user = await user_factory(test_session)
        await self._create_token(test_session, user)
        service = make_service(test_session)

        await service.logout(user.id, token="test-token-abc")

        result = await test_session.execute(
            sa_select(AccessToken).where(AccessToken.token == "test-token-abc")
        )
        token_row = result.scalar_one()
        assert token_row.is_active is False

    async def test_logout_without_token_deactivates_all(
        self, test_session, user_factory
    ):
        user = await user_factory(test_session)
        repo = AccessTokenRepository(test_session)
        for i in range(3):
            await repo.create(
                token=f"token-{i}",
                user_id=user.id,
                expires_at=datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
            )
        await test_session.commit()

        service = make_service(test_session)
        await service.logout(user.id)

        # All tokens should now be inactive; deactivate_all should return False (0 rows)
        result = await repo.deactivate_all_tokens(user.id)
        assert result is False

    async def test_logout_nonexistent_token_raises(self, test_session, user_factory):
        user = await user_factory(test_session)
        service = make_service(test_session)

        with pytest.raises(AccessTokenNotFound):
            await service.logout(user.id, token="does-not-exist")
