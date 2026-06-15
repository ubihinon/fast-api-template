import logging

from fastapi import APIRouter, Depends, HTTPException, status

from modules.notifications.services.users_email import UsersEmailService
from modules.notifications.settings import EmailSettings
from modules.users.dependencies import get_user_manager
from modules.users.exceptions import LoginCodeInvalidException, LoginMaxNumberAttemptsException, UserNotFoundException
from modules.users.fastapi_users_config import current_active_user
from modules.users.manager import UserManager
from modules.users.models import User
from modules.users.repositories import AccessTokenRepository
from modules.users.repositories.login_attempt import LoginAttemptRepository
from modules.users.repositories.login_code import LoginCodeRepository
from modules.users.repositories.user import UserRepository
from modules.users.schemas.requests import LoginWithEmailRequestSchema, VerifyLoginRequestSchema
from modules.users.schemas.responses import LoginResponse
from modules.users.services.auth_service import AuthMagicLinkService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


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
    # TODO ADD EXCEPTION HANDLING
    try:
        session = user_manager.user_db.session

        auth_service = AuthMagicLinkService(
            UserRepository(session),
            LoginCodeRepository(session),
            LoginAttemptRepository(session),
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
            LoginAttemptRepository(session),
            AccessTokenRepository(session),
            UsersEmailService(EmailSettings())
        )
        return await auth_service.verify_login_code(request.email, request.code)
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
