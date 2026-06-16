from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings


async def get_users_email_service() -> UsersEmailService:
    return UsersEmailService(EmailSettings())
