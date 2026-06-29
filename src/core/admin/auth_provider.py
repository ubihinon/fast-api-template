"""
Реализация AuthProvider для Starlette Admin
"""
import datetime
import logging
from typing import Optional

from sqlalchemy import select
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import FormValidationError, LoginFailed

from core.database import async_session
from .models import UserAdmin
from .utils import verify_password

logger = logging.getLogger(__name__)


class DatabaseAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if not username or len(username.strip()) == 0:
            raise FormValidationError(
                {"username": "Username must not be empty"}
            )

        if not password or len(password) == 0:
            raise FormValidationError(
                {"password": "Password must not be empty"}
            )

        async with async_session() as session:
            try:
                query = select(UserAdmin).where(
                    UserAdmin.username == username
                )
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user:
                    raise LoginFailed("Invalid username or password")

                if not user.is_active:
                    raise LoginFailed("User not active")

                if not verify_password(password, user.password_hash):
                    raise LoginFailed("Invalid username or password")

                user.last_login = datetime.datetime.now(datetime.UTC)
                session.commit()

                # 6. Сохранение пользователя в сессии
                request.session.update({
                    "user_id": user.id,
                    "username": user.username,
                    "is_superuser": user.is_superuser,
                })

                return response

            except Exception as e:
                logger.error(f"[Admin] Login error: {e}")
                await session.rollback()
                raise
            # finally:
            #     pass
                # db.close()

    async def is_authenticated(self, request: Request) -> bool:
        user_id = request.session.get("user_id")

        if not user_id:
            return False

        async with async_session() as session:
            try:
                query = select(UserAdmin).where(
                    UserAdmin.id == user_id
                )
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user or not user.is_active:
                    return False

                request.state.user = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "is_superuser": user.is_superuser,
                    "is_active": user.is_active,
                }

                return True
            except Exception as e:
                logger.error(f"[Admin] Authentication error: {e}")
                await session.rollback()
                raise
            # finally:
            #     db.close()

    def get_admin_user(self, request: Request) -> Optional[AdminUser]:
        """
        Возвращает информацию о пользователе для отображения в интерфейсе
        """
        user = getattr(request.state, "user", None)

        if not user:
            return None

        return AdminUser(
            username=user.get("username", "Unknown"),
            photo_url=None,  # Можно добавить URL аватара если нужно
        )

    def get_admin_config(self, request: Request) -> Optional[AdminConfig]:
        """
        Возвращает конфигурацию админки в зависимости от пользователя
        """
        user = getattr(request.state, "user", None)

        if not user:
            return None

        # Можно динамически менять заголовок и логотип в зависимости от пользователя
        custom_title = f"Админка - {user.get('full_name', user.get('username'))}"

        return AdminConfig(
            app_title=custom_title,
        )

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response
