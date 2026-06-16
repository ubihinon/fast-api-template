import pytest

from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings
from modules.users.settings import LOGIN_CODE_EXPIRES_IN_TIMEDELTA


@pytest.mark.unit
@pytest.mark.asyncio
class TestNotificationService:
    async def test_send_login_code_email(
        self,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)
        login_code = await login_code_factory(test_session, user.id)

        service = UsersEmailService(EmailSettings())
        result = await service.send_login_code_email(user.email, login_code.code, LOGIN_CODE_EXPIRES_IN_TIMEDELTA)
        assert result

    async def test_send_welcome_email(
        self,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)

        service = UsersEmailService(EmailSettings())
        result = await service.send_welcome_email(user.email)
        assert result

    async def test_send_welcome_email_task(
        self,
        test_session,
        user_factory,
        login_code_factory,
    ):
        user = await user_factory(test_session)

        service = UsersEmailService(EmailSettings())
        result = service.send_welcome_email_task(user.email)
        assert result
