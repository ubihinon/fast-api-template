"""Shared fixtures for notifications unit tests."""
from unittest.mock import AsyncMock

import pytest
from fastapi import BackgroundTasks
from fastapi_mail import FastMail

from modules.notifications.schemas.email_payload import EmailPayload
from modules.notifications.services.base_email import BaseEmailService
from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings


@pytest.fixture
def make_payload():
    def _make(**kwargs) -> EmailPayload:
        defaults = dict(
            recipients=["recipient@example.com"],
            subject="Test Subject",
            body={"key": "value"},
        )
        return EmailPayload(**{**defaults, **kwargs})
    return _make


@pytest.fixture
def background_tasks() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.fixture
def users_email_service(background_tasks) -> UsersEmailService:
    settings = EmailSettings(SUPPRESS_SEND=True)
    fastmail = FastMail(BaseEmailService.build_connection_config(settings))
    service = UsersEmailService(fastmail, background_tasks)
    # Patch fastmail to avoid any real network calls
    service.fastmail.send_message = AsyncMock(return_value=None)  # type: ignore[method-assign]
    return service
