import datetime

import pytest

from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings
from modules.users.dtos.auth import AccessTokenSchema
from modules.users.repositories import (
    AccessTokenRepository, LoginAttemptRepository, LoginCodeRepository,
    UserRepository,
)
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA


@pytest.mark.unit
@pytest.mark.asyncio
class TestVerifyLoginCodeService:
    async def test_verify_valid_login_code(
        self,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        login_code = await login_code_factory(test_session, user.id)

        service = AuthMagicLinkService(
            UserRepository(test_session),
            LoginCodeRepository(test_session),
            LoginAttemptRepository(test_session),
            AccessTokenRepository(test_session),
            UsersEmailService(EmailSettings()),
            '127.0.0.1',
        )
        access_token = await service.verify_login_code(user.email, login_code.code)

        expires_at = access_token.expires_at.replace(minute=0, second=0, microsecond=0)
        expected_expires_at = datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA
        expected_expires_at = expected_expires_at.replace(minute=0, second=0, microsecond=0)

        assert AccessTokenSchema.model_validate(access_token)
        assert access_token.token is not None
        assert access_token.is_active
        assert expires_at == expected_expires_at

    # async def test_verify_nonexistent_login_code(
    #     self,
    #     test_session,
    #     user_factory,
    # ):
    #     """Test verifying nonexistent login code."""
    #     # Arrange
    #     user = await user_factory(test_session)
    #     repository = LoginCodeRepository(test_session)
    #     service = VerifyLoginCodeService(repository)
    #
    #     # Act & Assert
    #     with pytest.raises(LoginCodeNotFoundError):
    #         await service.execute("invalid_code", user.id)
    #
    # async def test_verify_expired_login_code(
    #     self,
    #     test_session,
    #     user_factory,
    # ):
    #     """Test verifying expired login code."""
    #     # Arrange
    #     user = await user_factory(test_session)
    #
    #     # Создаем истекший код
    #     from src.modules.users.infrastructure.models import LoginCode
    #
    #     expired_code = LoginCode(
    #         code="123456",
    #         user_id=user.id,
    #         is_active=True,
    #         expires_at=datetime.now(datetime.UTC) - timedelta(minutes=1),
    #     )
    #     test_session.add(expired_code)
    #     await test_session.commit()
    #
    #     repository = LoginCodeRepository(test_session)
    #     service = VerifyLoginCodeService(repository)
    #
    #     # Act & Assert
    #     with pytest.raises(LoginCodeNotFoundError):
    #         await service.execute(expired_code.code, user.id)
    #
    # async def test_verify_deactivates_code(
    #     self,
    #     test_session,
    #     user_factory,
    #     login_code_factory,
    # ):
    #     """Test that verifying code deactivates it."""
    #     # Arrange
    #     user = await user_factory(test_session)
    #     login_code = await login_code_factory(test_session, user.id)
    #
    #     repository = LoginCodeRepository(test_session)
    #     service = VerifyLoginCodeService(repository)
    #
    #     # Act
    #     await service.execute(login_code.code, user.id)
    #
    #     # Assert
    #     deactivated_code = await repository.get_by_id(login_code.id)
    #     assert deactivated_code is not None
    #     assert deactivated_code.is_active is False
