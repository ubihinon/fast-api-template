import datetime
import logging
import secrets

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from core.database import get_session
from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings
from modules.users.dependencies import get_user_manager
from modules.users.exceptions import LoginCodeInvalidException, LoginMaxNumberAttemptsException, UserNotFoundException
from modules.users.fastapi_users_config import current_active_user
from modules.users.manager import UserManager
from modules.users.models import User
from modules.users.repositories import AccessTokenRepository
from modules.users.repositories.login_code import LoginCodeRepository
from modules.users.repositories.user import UserRepository
from modules.users.schemas.auth import LoginResponse, LoginWithEmailRequestSchema
from modules.users.schemas.login_code import VerifyLoginRequestSchema
from modules.users.schemas.user import UserCreate
from modules.users.services.auth_service import AuthMagicLinkService
from modules.users.settings import ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA, LOGIN_CODE_EXPIRES_IN_TIMEDELTA


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ==========================================================
# TODO MOVE LOGIC TO SERVICES
# ==========================================================


@router.post("/magic/login", response_model=LoginResponse)
async def login_with_magic_link(
    request: LoginWithEmailRequestSchema,
    user_manager: UserManager = Depends(get_user_manager),
):
    """
    Example:
    POST /magic/login
    {
        "email": "user@example.com"
    }

    Response:
    {
        "message": "Code sent to your email"
    }
    """
    try:
        session = user_manager.user_db.session

        auth_service = AuthMagicLinkService(
            UserRepository(session),
            LoginCodeRepository(session),
            AccessTokenRepository(session),
            UsersEmailService(EmailSettings()),
        )
        await auth_service.login(request.email)
        # user_repository = UserRepository(user_manager.user_db.session)
        # user = await user_repository.get_by_email(request.email)
        #
        # if user is None:
        #     await user_repository.create(request.email)
        #
        # if not user.is_active:
        #     return LoginResponse(
        #         message="Если этот email зарегистрирован, вы получите ссылку для входа"
        #     )
        #
        # login_token = await LoginTokenRepository(user_manager.user_db.session).generate(
        #     user_id=user.id,
        #     expires_at=datetime.now(datetime.UTC) + LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        # )
        # try:
        #     await send_login_link(user.email, login_token)
        #     print(f"✓ Email входа отправлен на {user.email}")
        # except Exception as e:
        #     print(f"✗ Ошибка отправки email: {e}")
        #     raise HTTPException(
        #         status_code=500,
        #         detail="Ошибка отправки email. Попробуйте позже."
        #     )

        return LoginResponse(message="Code sent to your email")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=500,
            detail="Something went wrong",
        )


@router.post("/magic/logout")
async def logout(
    user: User = Depends(current_active_user),
):
    return {"message": f"Пользователь {user.email} вышел из системы"}


@router.post("/magic/verify-login")
async def verify_login(
    request: VerifyLoginRequestSchema,
    user_manager: UserManager = Depends(get_user_manager),
):
    try:
        session = user_manager.user_db.session

        auth_service = AuthMagicLinkService(
            UserRepository(session),
            LoginCodeRepository(session),
            AccessTokenRepository(session),
            UsersEmailService(EmailSettings())
        )
        await auth_service.verify_login_code(request.email, request.code)
    except UserNotFoundException as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except LoginCodeInvalidException as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except LoginMaxNumberAttemptsException as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.exception(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
    # user_repository = UserRepository(user_manager.user_db.session, user_manager.user_db)
    #     login_code = await LoginCodeRepository(user_manager.user_db.session).get(token)
    #     user = await user_repository.get(login_code.user_id)
    #
    #     if not user.id or not user.email:
    #         raise ValueError("Code is incorrect")
    #
    #     # Шаг 2: Получаем пользователя из БД
    #     # user = await user_manager.user_db.get_by_email(user.email)
    #     user = await user_repository.get_by_email(user.email)
    #
    #     if user is None:
    #         raise ValueError("User not found")
    #
    #     # Шаг 3: Проверяем, активен ли пользователь
    #     if not user.is_active:
    #         pass
    #
    #     # Шаг 4: Генерируем access token и сохраняем в БД
    #     access_token = await AccessTokenRepository(user_manager.user_db.session).generate(
    #         user_id=user.id,
    #         expires_at=datetime.datetime.now(datetime.UTC) + ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA,
    #     )
    #
    #     print(f"✓ Пользователь {user.email} вошел через Magic Link")
    #     print(f"✓ Access token: {access_token[:20]}...")
# ----------------------------------
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
    #
    # except Exception as e:
    #     print(f"✗ Ошибка при входе: {e}")
    #     return JSONResponse(
    #         content={"error": "Ошибка при входе"},
    #         status_code=500
    #     )
