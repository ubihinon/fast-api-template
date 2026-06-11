import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import LoginCode
from modules.users.schemas.login_code import LoginCodeReadSchema, VerifyLoginRequestSchema


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

    async def get(self, code: str, user_id: UserIdType) -> LoginCodeReadSchema | None:
        query = select(LoginCode).where(
            LoginCode.code == code,
            LoginCode.user_id == user_id,
            LoginCode.is_active == True,
            LoginCode.expires_at > datetime.now(datetime.UTC)
        )
        result = await self.session.execute(query)
        login_code_record = result.scalar_one_or_none()

        return LoginCodeReadSchema.model_validate(login_code_record) if login_code_record else None

    async def deactivate(self, login_code: LoginCodeReadSchema) -> LoginCodeReadSchema:
        login_code.is_active = False
        await self.session.commit()

    async def increase_attempt(self, login_code: LoginCodeReadSchema) -> LoginCodeReadSchema:
        login_code.attempts += 1
        await self.session.commit()
        return  LoginCodeReadSchema.model_validate(login_code)
