import logging

from fastapi import Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from core.models.types import UserIdType
from core.settings import RESET_PASSWORD_TOKEN_SECRET, VERIFICATION_TOKEN_SECRET
from modules.users.models import User

logger = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret = VERIFICATION_TOKEN_SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        logger.warning("User %s has registered.", user.id)

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        logger.warning("Verification requested for user %s. Verification token: %s", user.id, token)
