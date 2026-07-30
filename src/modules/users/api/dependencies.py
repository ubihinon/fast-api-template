from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.dependencies import get_user_notification_service
from core.utils.http import get_client_ip
from modules.users.manager import UserManager
from modules.users.models import User
from modules.users.ports import UserNotificationPort
from modules.users.repositories import (
    AccessTokenRepository,
    LoginAttemptRepository,
    LoginCodeRepository,
)
from modules.users.services.auth_service import AuthMagicLinkService


async def get_auth_magic_link_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    email_service: Annotated[UserNotificationPort, Depends(get_user_notification_service)],
) -> AuthMagicLinkService:
    user_manager = UserManager(User.get_db(session), email_service)
    return AuthMagicLinkService(
        session=session,
        login_code_repository=LoginCodeRepository(session),
        login_attempt_repository=LoginAttemptRepository(session),
        access_token_repository=AccessTokenRepository(session),
        ip_address=get_client_ip(request),
        user_agent=(request.headers.get("user-agent") or "")[:512] or None,
        email_service=email_service,
        user_manager=user_manager,
    )
