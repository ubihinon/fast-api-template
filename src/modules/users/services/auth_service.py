import datetime
import logging
import secrets

from fastapi_users import exceptions

from modules.notifications.services.users_email import UsersEmailService
from modules.users.exceptions import (
    AuthErrorException, LoginCodeExpiredException, LoginCodeInactiveException, LoginCodeInvalidException,
    LoginMaxNumberAttemptsException,
    UserNotFoundException,
)
from modules.users.manager import UserManager
from modules.users.models import User
from modules.users.repositories import AccessTokenRepository
from modules.users.repositories.login_attempt import LoginAttemptRepository
from modules.users.repositories.login_code import LoginCodeRepository
from modules.users.repositories.user import UserRepository
from modules.users.schemas.user import UserCreate
from modules.users.settings import (
    ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA, LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
    MAX_LOGIN_ATTEMPTS,
)

logger = logging.getLogger(__name__)


class AuthMagicLinkService:
    def __init__(
        self,
        user_repository: UserRepository,
        login_code_repository: LoginCodeRepository,
        login_attempt_repository: LoginAttemptRepository,
        access_token_repository: AccessTokenRepository,
        email_service: UsersEmailService,
    ):
        self.user_repository = user_repository
        self.login_code_repository = login_code_repository
        self.login_attempt_repository = login_attempt_repository
        self.access_token_repository = access_token_repository
        self.email_service = email_service

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
        # await self.email_service.send_login_code_email(user.email, login_token)

        # try:
        #     await send_login_link(user.email, login_token)
        #     print(f"✓ Email входа отправлен на {user.email}")
        # except Exception as e:
        #     print(f"✗ Ошибка отправки email: {e}")
        #     raise HTTPException(
        #         status_code=500,
        #         detail="Ошибка отправки email. Попробуйте позже."
        #     )

        # user = await self.repository.create(email, name)
        return user

    def generate_code(self):
        random_number = secrets.randbelow(1000000)
        return str(random_number).zfill(6)

    async def verify_login_code(self, email: str, code: str):
        try:
            user = await self.user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            raise UserNotFoundException(email)

        failed_attempts_count = await self.login_attempt_repository.get_failed_attempts_count(code, user.id)

        if failed_attempts_count >= MAX_LOGIN_ATTEMPTS:
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address='127.0.0.1'
            )
            raise LoginMaxNumberAttemptsException(
                f"Maximum number of attempts exceeded ({MAX_LOGIN_ATTEMPTS}). Try again later"
            )

        login_code = await self.login_code_repository.get(code, user.id)
        if not login_code:
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address='127.0.0.1'
            )
            raise LoginCodeInvalidException(code)

        if login_code.is_expired():
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address='127.0.0.1'
            )
            raise LoginCodeExpiredException(code)

        if not login_code.is_active:
            await self.login_attempt_repository.create(
                user.id, user.email, code, False, ip_address='127.0.0.1'
            )
            raise LoginCodeInactiveException(code)

        await self.login_attempt_repository.create(user.id, user.email, code, True, ip_address='127.0.0.1')

        await self.login_code_repository.increase_attempt(login_code)

        logger.info(f"✓ Code {code} is correct for user_id={user.id}")

        access_token = await self.access_token_repository.generate(
            token=secrets.token_urlsafe(48),
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
        )

        await self.login_code_repository.deactivate(login_code)

        logger.info(f"✓ User {user.email} logged in via Magic Link")
        logger.info(f"✓ Access token: {access_token[:20]}...")

    # async def _verify_login_code(
    #     self,
    #     code: str,
    #     user_id: int,
    #     user_db,
    #     max_attempts: int = 5
    # ) -> bool:
    #     """
    #     Проверяет 6-значный код для входа.
    #
    #     Args:
    #         code: Код, введенный пользователем (например, "123456")
    #         user_id: ID пользователя
    #         user_db: SQLAlchemyUserDatabase
    #         max_attempts: Максимальное количество попыток
    #
    #     Returns:
    #         True если код верный, False если неверный
    #
    #     Raises:
    #         ValueError: Если код истек, деактивирован или превышены попытки
    #     """
    #
    #     session = user_db.session
    #
    #     try:
    #         # Ищем активный код
    #         query = select(LoginToken).where(
    #             LoginToken.code == code,
    #             LoginToken.user_id == user_id,
    #             LoginToken.is_active == True,
    #             LoginToken.expires_at > datetime.utcnow()
    #         )
    #         result = await session.execute(query)
    #         login_token = result.scalar_one_or_none()
    #
    #         # Если кода нет
    #         if not login_token:
    #             raise ValueError("Код неверный или истек")
    #
    #         # Проверяем количество попыток
    #         if login_token.attempts >= max_attempts:
    #             # Деактивируем код после превышения попыток
    #             login_token.is_active = False
    #             await session.commit()
    #             raise ValueError(f"Превышено максимальное количество попыток ({max_attempts})")
    #
    #         # Увеличиваем счетчик попыток
    #         login_token.attempts += 1
    #         await session.commit()
    #
    #         print(f"✓ Код {code} верный для user_id={user_id}")
    #         return True
    #
    #     except ValueError as e:
    #         print(f"✗ Ошибка проверки кода: {e}")
    #         raise
    #     except Exception as e:
    #         print(f"✗ Неожиданная ошибка: {e}")
    #         raise

    # """Вход по 6-значному коду."""
    # try:
    #     # Получаем пользователя
    #     user = await user_manager.user_db.get_by_email(request.email)
    #
    #     if user is None:
    #         raise ValueError("Пользователь не найден")
    #
    #     # Проверяем код
    #     try:
    #         await _verify_login_code(request.code, user.id, user_manager.user_db)
    #     except ValueError as e:
    #         return JSONResponse(
    #             content={"error": str(e)},
    #             status_code=400
    #         )
    #
    #     # Генерируем access token
    #     access_token = await _generate_access_token(
    #         user.id,
    #         user.email,
    #         user_manager.user_db
    #     )
    #
    #     # Деактивируем код после использования
    #     await _deactivate_login_code(request.code, user.id, user_manager.user_db)
    #
    #     print(f"✓ Пользователь {user.email} вошел с кодом")
    #
    #     return {
    #         "access_token": access_token,
    #         "token_type": "bearer",
    #         "user": {
    #             "id": str(user.id),
    #             "email": user.email
    #         }
    #     }

    async def get_user(self, email: str):
        user = await self.repository.get_by_email(email)
        return user

    async def get_user_by_id(self, user_id: int):
        user = await self.repository.get_by_id(user_id)
        return user

    async def get_users(self):
        users = await self.repository.all()
        return users
