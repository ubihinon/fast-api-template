import datetime
import logging
import secrets

from fastapi_users import exceptions
from sqlalchemy.ext.asyncio import AsyncSession

from core.i18n import _
from modules.notifications.services.users_email import UsersEmailService
from modules.users.settings import users_settings
from modules.users.dtos.auth import AccessTokenSchema
from modules.users.dtos.user import UserCreate
from modules.users.models.user import User
from modules.users.exceptions import (
    AccessTokenNotFound,
    AuthErrorException,
    LoginCodeInvalidException,
    LoginCodeNotFoundException,
    LoginMaxNumberAttemptsException,
    UserNotFoundException,
)
from modules.users.manager import UserManager
from modules.users.repositories import AccessTokenRepository
from modules.users.repositories.login_attempt import LoginAttemptRepository
from modules.users.repositories.login_code import LoginCodeRepository
from modules.users.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class AuthMagicLinkService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        login_code_repository: LoginCodeRepository,
        login_attempt_repository: LoginAttemptRepository,
        access_token_repository: AccessTokenRepository,
        email_service: UsersEmailService,
        user_manager: UserManager,
        ip_address: str,
    ):
        self.session = session
        self.user_repository = user_repository
        self.login_code_repository = login_code_repository
        self.login_attempt_repository = login_attempt_repository
        self.access_token_repository = access_token_repository
        self.email_service = email_service
        self.user_manager = user_manager
        self.ip_address = ip_address

    async def login(self, email: str) -> User:
        try:
            user = await self.user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            user_create = UserCreate(
                email=email,
                password=secrets.token_urlsafe(32),
                is_active=True,
                is_verified=True
            )
            user = await self.user_manager.create(user_create)

        if not user.is_active:
            raise AuthErrorException(_("User %(email)s is not active") % {"email": email})

        await self.login_code_repository.deactivate_all_for_user(user.id)
        login_code = await self.login_code_repository.create(
            user_id=user.id,
            code=self.generate_code(),
            expires_at=datetime.datetime.now(datetime.UTC) + users_settings.LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        )
        logger.info(f"Login code sent to {user.email}")
        self.email_service.send_login_code_email_task(
            user.email, login_code.code, users_settings.LOGIN_CODE_EXPIRES_IN_TIMEDELTA
        )

        await self.session.commit()

        return user

    async def verify_login_code(self, email: str, code: str) -> AccessTokenSchema:
        try:
            user = await self.user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            raise UserNotFoundException(email)

        failed_attempts_since = datetime.datetime.now(datetime.UTC) - users_settings.LOGIN_CODE_EXPIRES_IN_TIMEDELTA
        failed_attempts_count = await self.login_attempt_repository.get_failed_attempts_count(
            user.id, self.ip_address, since=failed_attempts_since
        )

        if failed_attempts_count >= users_settings.MAX_LOGIN_ATTEMPTS:
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address=self.ip_address
            )
            raise LoginMaxNumberAttemptsException(
                _("Maximum number of attempts exceeded (%(max)s). Try again later") % {"max": users_settings.MAX_LOGIN_ATTEMPTS}
            )

        login_code = await self.login_code_repository.get_active(code, user.id)
        if not login_code:
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address=self.ip_address
            )
            raise LoginCodeInvalidException()

        await self.login_attempt_repository.create(user.id, user.email, code, True, ip_address=self.ip_address)

        logger.info(f"✓ Code is correct for user_id={user.id}")

        access_token = await self.access_token_repository.create(
            token=secrets.token_urlsafe(48),
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC) + users_settings.ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
        )

        deactivated_code = await self.login_code_repository.deactivate(login_code.id)
        if deactivated_code is None:
            raise LoginCodeNotFoundException(login_code.id)

        logger.info(f"✓ User {user.email} logged in via Magic Link")

        await self.session.commit()

        return AccessTokenSchema.model_validate(access_token)

    async def logout(self, user_id: int, token: str | None = None) -> None:
        if token:
            if not await self.access_token_repository.deactivate_token(user_id, token):
                raise AccessTokenNotFound(_("Token not found"))
        else:
            await self.access_token_repository.deactivate_all_tokens(user_id)
        await self.session.commit()

    @staticmethod
    def generate_code():
        random_number = secrets.randbelow(1000000)
        return str(random_number).zfill(6)
