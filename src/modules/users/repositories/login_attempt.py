import datetime

from sqlalchemy import func, select

from core.models.types import UserIdType
from modules.users.models import LoginAttempt
from modules.users.repositories.base import BaseRepository


class LoginAttemptRepository(BaseRepository):
    async def create(
        self,
        user_id: UserIdType,
        email: str,
        code_entered: str,
        is_correct: bool,
        ip_address: str | None,
        user_agent: str | None = None,
    ) -> LoginAttempt:
        login_attempt = LoginAttempt(
            user_id=user_id,
            email=email,
            code_entered=code_entered,
            is_correct=is_correct,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self.session.add(login_attempt)
        await self.session.flush()
        return login_attempt

    async def get_history(
        self, user_id: UserIdType, limit: int = 50, offset: int = 0
    ) -> list[LoginAttempt]:
        result = await self.session.execute(
            select(LoginAttempt)
            .where(LoginAttempt.user_id == user_id)
            .order_by(LoginAttempt.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def get_failed_attempts_count(
        self, user_id: UserIdType, since: datetime.datetime
    ) -> int:
        query = select(func.count()).select_from(LoginAttempt).where(
            LoginAttempt.user_id == user_id,
            LoginAttempt.is_correct.is_(False),
            LoginAttempt.created_at >= since,
        )
        return await self.session.scalar(query) or 0
