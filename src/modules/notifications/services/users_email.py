import datetime
from fastapi import BackgroundTasks

from .base_email import BaseEmailService, EmailPayload
from ..settings import EmailSettings


class UsersEmailService(BaseEmailService):
    def __init__(self, settings: EmailSettings, background_tasks: BackgroundTasks):
        super().__init__(settings, background_tasks)

    async def send_login_code_email(self, email: str, login_code: str, expires_in: datetime.timedelta) -> bool:
        payload = EmailPayload(
            recipients=[email],
            subject="Login code",
            body={'email': email, "code": login_code, 'code_expires_in': expires_in},
        )
        return await self.send_email_async(payload, template_name="users/login_code.html")

    async def send_welcome_email(self, email: str) -> bool:
        payload = EmailPayload(
            recipients=[email],
            subject="Welcome to our service!",
            body={'email': email, "action_url": "https://example.com/dashboard"},
        )
        return await self.send_email_async(payload, template_name="users/welcome.html")

    def send_login_code_email_task(self, email: str, login_code: str, expires_in: datetime.timedelta) -> bool:
        payload = EmailPayload(
            recipients=[email],
            subject="Login code",
            body={'email': email, "code": login_code, 'code_expires_in': expires_in},
        )
        return self.send_email_background(payload, template_name="users/login_code.html")

    def send_welcome_email_task(self, email: str) -> bool:
        payload = EmailPayload(
            recipients=[email],
            subject="Welcome to our service!",
            body={'email': email, "action_url": "https://example.com/dashboard"},
        )
        return self.send_email_background(payload, template_name="users/welcome.html")
