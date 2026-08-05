from fastapi import BackgroundTasks
from fastapi_mail import FastMail

from modules.notifications.services.base_email import BaseEmailService
from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import email_settings

_fastmail = FastMail(BaseEmailService.build_connection_config(email_settings))


async def get_users_email_service(background_tasks: BackgroundTasks) -> UsersEmailService:
    return UsersEmailService(_fastmail, background_tasks)
