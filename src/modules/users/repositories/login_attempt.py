import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import LoginAttempt
from modules.users.schemas.login_attempt import LoginAttemptReadSchema
from modules.users.settings import LOGIN_CODE_EXPIRES_IN_TIMEDELTA


class LoginAttemptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, user_id: UserIdType, email: str,  code_entered: str, is_correct: bool, ip_address: str
    ) -> LoginAttemptReadSchema:
        login_code = LoginAttempt(
            user_id=user_id,
            email=email,
            code_entered=code_entered,
            is_correct=is_correct,
            ip_address=ip_address,
        )
        self.session.add(login_code)
        await self.session.commit()
        return LoginAttemptReadSchema.model_validate(login_code)

    async def get_failed_attempts_count(self, code: str, user_id: UserIdType) -> int:
        query = select(LoginAttempt).where(
            LoginAttempt.code == code,
            LoginAttempt.user_id == user_id,
            LoginAttempt.is_correct == False,
            LoginAttempt.created_at >= (datetime.now(datetime.UTC) - LOGIN_CODE_EXPIRES_IN_TIMEDELTA)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0
