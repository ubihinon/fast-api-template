import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import LoginCode
from modules.users.dtos.auth import LoginCodeReadSchema
from modules.users.repositories.base import BaseRepository


class LoginCodeRepository(BaseRepository):
    async def create(self, user_id: UserIdType, code: str, expires_at: datetime.datetime) -> LoginCodeReadSchema:
        login_code = LoginCode(
            code=code,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(login_code)
        await self.session.flush()
        return LoginCodeReadSchema.model_validate(login_code)

    async def get_active(self, code: str, user_id: UserIdType) -> LoginCodeReadSchema | None:
        query = select(LoginCode).where(
            LoginCode.code == code,
            LoginCode.user_id == user_id,
            LoginCode.is_active.is_(True),
            LoginCode.expires_at > datetime.datetime.now(datetime.UTC)
        )
        result = await self.session.execute(query)
        login_code = result.scalar_one_or_none()
        return LoginCodeReadSchema.model_validate(login_code) if login_code else None

    async def deactivate(self, code_id: int) -> LoginCodeReadSchema | None:
        result = await self.session.execute(
            update(LoginCode)
            .where(LoginCode.id == code_id)
            .values(is_active=False)
            .returning(LoginCode)
        )
        await self.session.flush()
        login_code = result.scalar_one_or_none()
        return LoginCodeReadSchema.model_validate(login_code) if login_code else None
