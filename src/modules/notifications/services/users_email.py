from typing import Any, Dict, Optional
from fastapi import BackgroundTasks
from pydantic import EmailStr

from .base_email import BaseEmailService, EmailPayload
from ..settings import EmailSettings


class UsersEmailService(BaseEmailService):
    def __init__(self, settings: EmailSettings):
        super().__init__(settings)

    async def send_login_code_email(self, email: EmailStr) -> bool:
        """
        Асинхронная отправка приветственного письма новому пользователю с использованием HTML-шаблона.
        """
        payload = EmailPayload(
            recipients=[email],
            subject="Добро пожаловать в наш сервис!",
            body={
                "action_url": "https://example.com/dashboard"
            }
        )
        return await self.send_email_async(payload, template_name="welcome.html")


    async def send_welcome_email(self, email: EmailStr) -> bool:
        """
        Асинхронная отправка приветственного письма новому пользователю с использованием HTML-шаблона.
        """
        payload = EmailPayload(
            recipients=[email],
            subject="Добро пожаловать в наш сервис!",
            body={
                "action_url": "https://example.com/dashboard"
            }
        )
        return await self.send_email_async(payload, template_name="welcome.html")

    # def send_password_reset_background(
    #     self,
    #     background_tasks: BackgroundTasks,
    #     email: EmailStr,
    #     reset_token: str
    # ) -> None:
    #     """
    #     Отправка письма для сброса пароля в фоновом режиме (BackgroundTasks).
    #     """
    #     payload = EmailPayload(
    #         recipients=[email],
    #         subject="Восстановление доступа к аккаунту",
    #         body={
    #             "reset_url": f"https://example.com/reset-password?token={reset_token}"
    #         }
    #     )
    #     # Добавляем задачу отправки в фоновые задачи FastAPI
    #     self.send_email_background(
    #         background_tasks=background_tasks,
    #         payload=payload,
    #         template_name="password_reset.html"
    #     )
