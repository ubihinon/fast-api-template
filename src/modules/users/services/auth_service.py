# from datetime import datetime
import datetime

from modules.notifications.services.base_email import BaseEmailService
from modules.users.exceptions import AuthErrorException
from modules.users.repositories.login_token import LoginTokenRepository
from modules.users.repositories.user import UserRepository
from modules.users.settings import LOGIN_TOKEN_EXPIRES_IN_TIMEDELTA


class AuthMagicLinkService:
    def __init__(
        self,
        user_repository: UserRepository,
        login_token_repository: LoginTokenRepository,
        email_service: BaseEmailService
    ):
        self.user_repository = user_repository
        self.login_token_repository = login_token_repository
        self.email_service = email_service

    async def login(self, email: str):
        user = await self.user_repository.get_by_email(email)

        if user is None:
            await self.user_repository.create(email)

        if not user.is_active:
            raise AuthErrorException("User is not active")

        login_token = await self.login_token_repository.generate(
            user_id=user.id,
            expires_at=datetime.datetime.now(datetime.UTC) + LOGIN_TOKEN_EXPIRES_IN_TIMEDELTA,
        )

        self.email_service.send_login_code_email(user.email, login_token)
        # send_login_link(user.email, login_token)

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
        # return user

    async def get_user(self, email: str):
        user = await self.repository.get_by_email(email)
        return user

    async def get_user_by_id(self, user_id: int):
        user = await self.repository.get_by_id(user_id)
        return user

    async def get_users(self):
        users = await self.repository.all()
        return users
