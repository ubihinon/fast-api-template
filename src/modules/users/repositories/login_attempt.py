import datetime

from sqlalchemy import func, select

from core.models.types import UserIdType
from modules.users.models import LoginAttempt
from modules.users.repositories.base import BaseRepository


class LoginAttemptRepository(BaseRepository):
    async def create(
        self, user_id: UserIdType, email: str, code_entered: str, is_correct: bool, ip_address: str | None
    ) -> LoginAttempt:
        login_attempt = LoginAttempt(
            user_id=user_id,
            email=email,
            code_entered=code_entered,
            is_correct=is_correct,
            ip_address=ip_address,
        )
        self.session.add(login_attempt)
        await self.session.flush()
        return login_attempt

    async def get_failed_attempts_count(
        self, user_id: UserIdType, ip_address: str | None, since: datetime.datetime
    ) -> int:
        ip_filter = (
            LoginAttempt.ip_address.is_(None)
            if ip_address is None
            else LoginAttempt.ip_address == ip_address
        )
        query = select(func.count()).select_from(LoginAttempt).where(
            LoginAttempt.user_id == user_id,
            LoginAttempt.is_correct.is_(False),
            LoginAttempt.created_at >= since,
            ip_filter,
        )
        return await self.session.scalar(query) or 0
