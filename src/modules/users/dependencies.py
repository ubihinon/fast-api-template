from typing import Annotated

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from modules.notifications.dependencies import get_users_email_service
from modules.notifications.services.users_email import UsersEmailService
from modules.users.manager import UserManager
from modules.users.models import AccessToken, User


async def get_user_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield User.get_db(session)


async def get_user_manager(
    user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)],
    email_service: Annotated[UsersEmailService, Depends(get_users_email_service)],
):
    yield UserManager(user_db, email_service)


async def get_access_token_db(session: Annotated[AsyncSession, Depends(get_session)]):
    yield AccessToken.get_db(session)
