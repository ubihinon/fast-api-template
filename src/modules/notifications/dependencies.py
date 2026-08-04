from fastapi import BackgroundTasks

from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import email_settings


async def get_users_email_service(background_tasks: BackgroundTasks) -> UsersEmailService:
    return UsersEmailService(email_settings, background_tasks)
