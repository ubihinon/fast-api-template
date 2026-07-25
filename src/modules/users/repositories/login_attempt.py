import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import LoginAttempt
from modules.users.dtos.auth import LoginAttemptReadSchema
from modules.users.repositories.base import BaseRepository
from modules.users.settings import LOGIN_CODE_EXPIRES_IN_TIMEDELTA


class LoginAttemptRepository(BaseRepository):
    async def create(
        self, user_id: UserIdType, email: str, code_entered: str, is_correct: bool, ip_address: str
    ) -> LoginAttemptReadSchema:
        login_attempt = LoginAttempt(
            user_id=user_id,
            email=email,
            code_entered=code_entered,
            is_correct=is_correct,
            ip_address=ip_address,
        )
        self.session.add(login_attempt)
        await self.session.flush()
        return LoginAttemptReadSchema.model_validate(login_attempt)

    async def get_failed_attempts_count(self, code: str, user_id: UserIdType, ip_address: str) -> int:
        query = select(func.count()).select_from(LoginAttempt).where(
            LoginAttempt.code_entered == code,
            LoginAttempt.user_id == user_id,
            LoginAttempt.is_correct.is_(False),
            LoginAttempt.created_at >= (datetime.datetime.now(datetime.UTC) - LOGIN_CODE_EXPIRES_IN_TIMEDELTA),
            LoginAttempt.ip_address == ip_address,
        )
        return await self.session.scalar(query)
