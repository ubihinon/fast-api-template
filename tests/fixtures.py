import datetime
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import LoginCode, User
from modules.users.settings import LOGIN_CODE_EXPIRES_IN_TIMEDELTA


@pytest_asyncio.fixture
async def user_factory():
    async def _create_user(
        session: AsyncSession,
        email: str = "test@example.com",
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        user = User(
            email=email,
            hashed_password="password123",
            is_active=is_active,
            is_superuser=is_superuser,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    return _create_user


@pytest_asyncio.fixture
async def login_code_factory():
    """Factory for creating test login codes."""

    async def _create_login_code(
        session: AsyncSession,
        user_id: UserIdType,
        code: str = "123456",
        is_active: bool = True,
    ) -> LoginCode:
        login_code = LoginCode(
            code=code,
            user_id=user_id,
            is_active=is_active,
            expires_at=datetime.datetime.now(datetime.UTC) + LOGIN_CODE_EXPIRES_IN_TIMEDELTA,
        )
        session.add(login_code)
        await session.commit()
        await session.refresh(login_code)
        return login_code

    return _create_login_code
