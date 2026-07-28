"""Unit tests for UsersEmailService."""
from unittest.mock import AsyncMock

import pytest

from core.settings import settings
from modules.notifications.services.users_email import UsersEmailService

EMAIL = "user@example.com"
CODE = "123456"
EXPIRES_IN = settings.LOGIN_CODE_EXPIRES_IN_TIMEDELTA


@pytest.mark.unit
@pytest.mark.asyncio
class TestSendLoginCodeEmail:
    async def test_returns_true_on_success(self, users_email_service: UsersEmailService):
        result = await users_email_service.send_login_code_email(EMAIL, CODE, EXPIRES_IN)
        assert result is True

    async def test_passes_correct_template(self, users_email_service: UsersEmailService):
        await users_email_service.send_login_code_email(EMAIL, CODE, EXPIRES_IN)
        _, kwargs = users_email_service.fastmail.send_message.call_args  # type: ignore[attr-defined]
        assert kwargs.get("template_name") == "users/login_code.html"

    async def test_sends_to_correct_recipient(self, users_email_service: UsersEmailService):
        await users_email_service.send_login_code_email(EMAIL, CODE, EXPIRES_IN)
        msg = users_email_service.fastmail.send_message.call_args[0][0]  # type: ignore[attr-defined]
        assert EMAIL in str(msg.recipients)

    async def test_returns_false_on_smtp_error(self, users_email_service: UsersEmailService):
        from fastapi_mail.errors import ConnectionErrors
        users_email_service.fastmail.send_message = AsyncMock(  # type: ignore[method-assign]
            side_effect=ConnectionErrors("SMTP error")
        )
        result = await users_email_service.send_login_code_email(EMAIL, CODE, EXPIRES_IN)
        assert result is False


@pytest.mark.unit
@pytest.mark.asyncio
class TestSendWelcomeEmail:
    async def test_returns_true_on_success(self, users_email_service: UsersEmailService):
        result = await users_email_service.send_welcome_email(EMAIL)
        assert result is True

    async def test_passes_correct_template(self, users_email_service: UsersEmailService):
        await users_email_service.send_welcome_email(EMAIL)
        _, kwargs = users_email_service.fastmail.send_message.call_args  # type: ignore[attr-defined]
        assert kwargs.get("template_name") == "users/welcome.html"

    async def test_sends_to_correct_recipient(self, users_email_service: UsersEmailService):
        await users_email_service.send_welcome_email(EMAIL)
        msg = users_email_service.fastmail.send_message.call_args[0][0]  # type: ignore[attr-defined]
        assert EMAIL in str(msg.recipients)

    async def test_returns_false_on_smtp_error(self, users_email_service: UsersEmailService):
        from fastapi_mail.errors import ConnectionErrors
        users_email_service.fastmail.send_message = AsyncMock(  # type: ignore[method-assign]
            side_effect=ConnectionErrors("SMTP error")
        )
        result = await users_email_service.send_welcome_email(EMAIL)
        assert result is False


@pytest.mark.unit
class TestSendLoginCodeEmailTask:
    def test_adds_task_to_background_tasks(self, users_email_service: UsersEmailService):
        before = len(users_email_service.background_tasks.tasks)
        users_email_service.send_login_code_email_task(EMAIL, CODE, EXPIRES_IN)
        assert len(users_email_service.background_tasks.tasks) == before + 1

    def test_returns_task_list(self, users_email_service: UsersEmailService):
        result = users_email_service.send_login_code_email_task(EMAIL, CODE, EXPIRES_IN)
        assert isinstance(result, list)


@pytest.mark.unit
class TestSendWelcomeEmailTask:
    def test_adds_task_to_background_tasks(self, users_email_service: UsersEmailService):
        before = len(users_email_service.background_tasks.tasks)
        users_email_service.send_welcome_email_task(EMAIL)
        assert len(users_email_service.background_tasks.tasks) == before + 1

    def test_returns_task_list(self, users_email_service: UsersEmailService):
        result = users_email_service.send_welcome_email_task(EMAIL)
        assert isinstance(result, list)
