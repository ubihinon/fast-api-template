import datetime

from fastapi import BackgroundTasks
from fastapi_mail import FastMail

from core.i18n import _
from modules.notifications.template_renderer import render_email_template

from .base_email import BaseEmailService


class UsersEmailService(BaseEmailService):
    def __init__(self, fastmail: FastMail, background_tasks: BackgroundTasks):
        super().__init__(fastmail, background_tasks)

    async def send_login_code_email(self, email: str, login_code: str, expires_in: datetime.timedelta) -> bool:
        html = render_email_template("users/login_code.html", {
            "email": email,
            "code": login_code,
            "code_expires_in": expires_in,
        })
        return await self.send_rendered_email_async(
            recipients=[email],
            subject=_("Login code"),
            html=html,
        )

    async def send_welcome_email(self, email: str) -> bool:
        html = render_email_template("users/welcome.html", {"email": email})
        return await self.send_rendered_email_async(
            recipients=[email],
            subject=_("Welcome to our service!"),
            html=html,
        )

    def send_login_code_email_task(self, email: str, login_code: str, expires_in: datetime.timedelta) -> list:
        html = render_email_template("users/login_code.html", {
            "email": email,
            "code": login_code,
            "code_expires_in": expires_in,
        })
        return self.send_rendered_email_background(
            recipients=[email],
            subject=_("Login code"),
            html=html,
        )

    def send_welcome_email_task(self, email: str) -> list:
        html = render_email_template("users/welcome.html", {"email": email})
        return self.send_rendered_email_background(
            recipients=[email],
            subject=_("Welcome to our service!"),
            html=html,
        )
