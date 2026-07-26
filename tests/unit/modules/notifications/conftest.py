"""Shared fixtures for notifications unit tests."""
from unittest.mock import AsyncMock

import pytest
from fastapi import BackgroundTasks

from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings


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
    service.fastmail.send_message = AsyncMock(return_value=None)
    return service
