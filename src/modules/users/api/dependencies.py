from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.utils.http import get_client_ip
from modules.notifications.dependencies import get_users_email_service
from modules.notifications.services.users_email import UsersEmailService
from modules.users.repositories import (
    AccessTokenRepository,
    LoginAttemptRepository,
    LoginCodeRepository,
    UserRepository,
)
from modules.users.services.auth_service import AuthMagicLinkService


async def get_auth_magic_link_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
    email_service: Annotated[UsersEmailService, Depends(get_users_email_service)],
) -> AuthMagicLinkService:
    return AuthMagicLinkService(
        session=session,
        user_repository=UserRepository(session),
        login_code_repository=LoginCodeRepository(session),
        login_attempt_repository=LoginAttemptRepository(session),
        access_token_repository=AccessTokenRepository(session),
        ip_address=get_client_ip(request),
        email_service=email_service,
    )
