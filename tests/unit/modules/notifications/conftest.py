"""Shared fixtures for notifications unit tests."""
from unittest.mock import AsyncMock

import pytest
from fastapi import BackgroundTasks

from modules.notifications.schemas.email_payload import EmailPayload
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
def email_settings() -> EmailSettings:
    """EmailSettings with SUPPRESS_SEND=True to avoid real SMTP calls."""
    return EmailSettings(SUPPRESS_SEND=True)


@pytest.fixture
def background_tasks() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.fixture
def users_email_service(email_settings, background_tasks) -> UsersEmailService:
    service = UsersEmailService(email_settings, background_tasks)
    # Patch fastmail to avoid any real network calls
    service.fastmail.send_message = AsyncMock(return_value=None)  # type: ignore[method-assign]
    return service
