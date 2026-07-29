"""Unit tests for BaseEmailService."""
from unittest.mock import AsyncMock

import pytest
from fastapi_mail.errors import ConnectionErrors

from modules.notifications.schemas.email_payload import EmailPayload
from modules.notifications.services.users_email import UsersEmailService


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


@pytest.mark.unit
class TestPrepareMessage:
    def test_subject_and_recipients_are_set(self, users_email_service: UsersEmailService, make_payload):
        payload = make_payload(subject="Hello", recipients=["a@b.com"])
        msg = users_email_service._prepare_message(payload)
        assert msg.subject == "Hello"
        assert "a@b.com" in str(msg.recipients)

    def test_optional_fields_default_to_empty(self, users_email_service: UsersEmailService, make_payload):
        payload = make_payload()
        msg = users_email_service._prepare_message(payload)
        assert msg.attachments == []
        assert msg.cc == []
        assert msg.bcc == []
        assert msg.reply_to == []

    def test_cc_bcc_reply_to_are_forwarded(self, users_email_service: UsersEmailService, make_payload):
        payload = make_payload(
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            reply_to=["reply@example.com"],
        )
        msg = users_email_service._prepare_message(payload)
        assert "cc@example.com" in str(msg.cc)
        assert "bcc@example.com" in str(msg.bcc)
        assert "reply@example.com" in str(msg.reply_to)


@pytest.mark.unit
class TestSendEmailAsync:
    async def test_returns_true_on_success(self, users_email_service: UsersEmailService, make_payload):
        result = await users_email_service.send_email_async(make_payload())
        assert result is True

    async def test_calls_fastmail_send_message(self, users_email_service: UsersEmailService, make_payload):
        payload = make_payload()
        await users_email_service.send_email_async(payload, template_name="tmpl.html")
        users_email_service.fastmail.send_message.assert_awaited_once()  # type: ignore[attr-defined]

    async def test_returns_false_on_connection_error(self, users_email_service: UsersEmailService, make_payload):
        users_email_service.fastmail.send_message = AsyncMock(  # type: ignore[method-assign]
            side_effect=ConnectionErrors("SMTP unreachable")
        )
        result = await users_email_service.send_email_async(make_payload())
        assert result is False

    async def test_returns_false_on_unexpected_error(self, users_email_service: UsersEmailService, make_payload):
        users_email_service.fastmail.send_message = AsyncMock(  # type: ignore[method-assign]
            side_effect=RuntimeError("boom")
        )
        result = await users_email_service.send_email_async(make_payload())
        assert result is False


@pytest.mark.unit
class TestSendEmailBackground:
    def test_adds_task_to_background_tasks(self, users_email_service: UsersEmailService, make_payload):
        before = len(users_email_service.background_tasks.tasks)
        users_email_service.send_email_background(make_payload())
        assert len(users_email_service.background_tasks.tasks) == before + 1

    def test_returns_task_list(self, users_email_service: UsersEmailService, make_payload):
        result = users_email_service.send_email_background(make_payload())
        assert isinstance(result, list)
        assert len(result) >= 1
