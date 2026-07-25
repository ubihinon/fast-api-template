import datetime
import logging
import secrets

from fastapi_users import exceptions

from modules.notifications.services.users_email import UsersEmailService
from modules.users.dtos.auth import AccessTokenSchema
from modules.users.exceptions import (
    AccessTokenNotFound, AuthErrorException, LoginCodeInvalidException,
    LoginCodeNotFoundException, LoginMaxNumberAttemptsException,
    UserNotFoundException,
)
from modules.users.manager import UserManager
from modules.users.models import User
from modules.users.repositories import AccessTokenRepository
from modules.users.repositories.login_attempt import LoginAttemptRepository
from modules.users.repositories.login_code import LoginCodeRepository
from modules.users.repositories.user import UserRepository
from modules.users.dtos.user import UserCreate
from modules.users.settings import (
    ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA, LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
    MAX_LOGIN_ATTEMPTS,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AuthMagicLinkService:
    def __init__(
        self,
        user_repository: UserRepository,
        login_code_repository: LoginCodeRepository,
        login_attempt_repository: LoginAttemptRepository,
        access_token_repository: AccessTokenRepository,
        email_service: UsersEmailService,
        ip_address: str,
    ):
        self.user_repository = user_repository
        self.login_code_repository = login_code_repository
        self.login_attempt_repository = login_attempt_repository
        self.access_token_repository = access_token_repository
        self.email_service = email_service
        self.ip_address = ip_address

        user_db = User.get_db(user_repository.session)
        self.user_manager = UserManager(user_db)

    async def login(self, email: str):
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
            raise AuthErrorException(f"User {email} is not active")

        login_code = await self.login_code_repository.create(
            user_id=user.id,
            code=self.generate_code(),
            expires_at=datetime.datetime.now(datetime.UTC) + LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        )
        logger.info(f"Login code sent to {user.email}")
        self.email_service.send_login_code_email_task(user.email, login_code.code, LOGIN_CODE_EXPIRES_IN_TIMEDELTA)

        return user

    def generate_code(self):
        random_number = secrets.randbelow(1000000)
        return str(random_number).zfill(6)

    async def verify_login_code(self, email: str, code: str) -> AccessTokenSchema:
        try:
            user = await self.user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            raise UserNotFoundException(email)

        failed_attempts_count = await self.login_attempt_repository.get_failed_attempts_count(
            code, user.id, self.ip_address
        )

        if failed_attempts_count >= MAX_LOGIN_ATTEMPTS:
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address=self.ip_address
            )
            raise LoginMaxNumberAttemptsException(
                f"Maximum number of attempts exceeded ({MAX_LOGIN_ATTEMPTS}). Try again later"
            )

        login_code = await self.login_code_repository.get_active(code, user.id)
        if not login_code:
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address=self.ip_address
            )
            raise LoginCodeInvalidException(code)

        await self.login_attempt_repository.create(user.id, user.email, code, True, ip_address=self.ip_address)

        logger.info(f"✓ Code {code} is correct for user_id={user.id}")

        access_token = await self.access_token_repository.generate(
            token=secrets.token_urlsafe(48),
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
        )

        is_deactivated = await self.login_code_repository.deactivate(login_code.id)
        if is_deactivated is None:
            raise LoginCodeNotFoundException()

        logger.info(f"✓ User {user.email} logged in via Magic Link")
        logger.info(f"✓ Access token: {access_token.token[:10]}...")

        return access_token

    async def logout(self, user_id: int, token: str | None = None):
        if token:
            if not await self.access_token_repository.deactivate_token(user_id, token):
                raise AccessTokenNotFound("Token not found")
        else:
            await self.access_token_repository.deactivate_all_tokens(user_id)

    # async def get_user(self, email: str):
    #     user = await self.user_repository.get_by_email(email)
    #     return user
    #
    # async def get_user_by_id(self, user_id: int):
    #     user = await self.user_repository.get_by_id(user_id)
    #     return user
    #
    # async def get_users(self):
    #     users = await self.user_repository.all()
    #     return users
