import logging

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from core.models.types import UserIdType
from modules.notifications.services.users_email import UsersEmailService
from modules.users.settings import users_settings
from modules.users.models import User

logger = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = users_settings.RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret = users_settings.VERIFICATION_TOKEN_SECRET

    def __init__(self, user_db, email_service: UsersEmailService):
        super().__init__(user_db)
        self.email_service = email_service

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.warning("User %s has registered.", user.id)
        self.email_service.send_welcome_email_task(user.email)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        logger.warning("Verification requested for user %s.", user.id)
