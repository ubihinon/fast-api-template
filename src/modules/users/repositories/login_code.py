import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import LoginCode
from modules.users.dtos.auth import LoginCodeReadSchema


class LoginCodeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UserIdType, code: str, expires_at: datetime.datetime) -> LoginCodeReadSchema:
        login_code = LoginCode(
            code=code,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(login_code)
        await self.session.commit()
        return LoginCodeReadSchema.model_validate(login_code)

    async def get_active(self, code: str, user_id: UserIdType) -> LoginCodeReadSchema | None:
        query = select(LoginCode).where(
            LoginCode.code == code,
            LoginCode.user_id == user_id,
            LoginCode.is_active == True,
            LoginCode.expires_at > datetime.datetime.now(datetime.UTC)
        )
        result = await self.session.execute(query)
        login_code_record = result.scalar_one_or_none()

        return LoginCodeReadSchema.model_validate(login_code_record) if login_code_record else None

    async def deactivate(self, code_id: int) -> LoginCodeReadSchema | None:
        query = select(LoginCode).where(LoginCode.id == code_id)
        result = await self.session.execute(query)
        login_code = result.scalar_one_or_none()

        if login_code is None:
            return None

        login_code.is_active = False
        await self.session.commit()
        await self.session.refresh(login_code)

        return LoginCodeReadSchema.model_validate(login_code)
