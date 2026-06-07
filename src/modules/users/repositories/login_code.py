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

    async def get(self, code: str) -> VerifyLoginRequestSchema:
        query = select(LoginCode).where(
            LoginCode.code == code,
            LoginCode.is_active == True,
            LoginCode.expires_at > datetime.now(datetime.UTC)
        )
        result = await self.session.execute(query)
        login_code_record = result.scalar_one_or_none()

        if not login_code_record:
            raise ValueError("Code is invalid or expired")

        return VerifyLoginRequestSchema.model_validate(login_code_record)
