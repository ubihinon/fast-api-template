import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from modules.users.api.dependencies import get_auth_magic_link_service
from modules.users.exceptions import (
    AuthErrorException, LoginCodeInvalidException, LoginMaxNumberAttemptsException,
    UserNotFoundException,
)
from modules.users.fastapi_users_config import current_active_user
from modules.users.models import User
from modules.users.schemas.requests import LoginWithEmailRequestSchema, VerifyLoginRequestSchema
from modules.users.schemas.responses import LoginAccessTokenResponseSchema, LoginResponse
from modules.users.services.auth_service import AuthMagicLinkService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/magic/login", response_model=LoginResponse)
async def login_with_magic_link(
    request_data: LoginWithEmailRequestSchema,
    auth_service: Annotated[AuthMagicLinkService, Depends(get_auth_magic_link_service)]
) -> LoginResponse:
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
        await auth_service.login(request_data.email)
        return LoginResponse(message="Code sent to your email")
    except AuthErrorException as e:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=str(e))
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
    request_data: VerifyLoginRequestSchema,
    auth_service: Annotated[AuthMagicLinkService, Depends(get_auth_magic_link_service)]
) -> LoginAccessTokenResponseSchema:
    try:
        access_token = await auth_service.verify_login_code(request_data.email, request_data.code)
        return LoginAccessTokenResponseSchema.model_validate({'access_token': access_token.token})
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
