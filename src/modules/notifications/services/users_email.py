from typing import Any, Dict, Optional
from fastapi import BackgroundTasks
from pydantic import NameEmail

from .base_email import BaseEmailService, EmailPayload
from ..settings import EmailSettings
from ...users.settings import LOGIN_CODE_EXPIRES_IN_TIMEDELTA


class UsersEmailService(BaseEmailService):
    def __init__(self, settings: EmailSettings):
        super().__init__(settings)

    async def send_login_code_email(self, email: NameEmail, login_code: str) -> bool:
        payload = EmailPayload(
            recipients=[email],
            subject="Login code",
            body={'email': email, "code": login_code, 'code_expires_in': LOGIN_CODE_EXPIRES_IN_TIMEDELTA},
        )
        return await self.send_email_async(payload, template_name="users/login_code.html")

    async def send_welcome_email(self, email: NameEmail) -> bool:
        payload = EmailPayload(
            recipients=[email],
            subject="Welcome to our service!",
            body={'email': email, "action_url": "https://example.com/dashboard"},
        )
        return await self.send_email_async(payload, template_name="users/welcome.html")

    def send_welcome_email_task(self, email: NameEmail) -> bool:
        payload = EmailPayload(
            recipients=[email],
            subject="Welcome to our service!",
            body={'email': email, "action_url": "https://example.com/dashboard"},
        )
        return self.send_email_background(BackgroundTasks(), payload, template_name="users/welcome.html")
