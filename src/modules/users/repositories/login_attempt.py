import datetime

from sqlalchemy import func, select

from core.models.types import UserIdType
from modules.users.models import LoginAttempt
from modules.users.settings import users_settings
from modules.users.repositories.base import BaseRepository


class LoginAttemptRepository(BaseRepository):
    async def create(
        self, user_id: UserIdType, email: str, code_entered: str, is_correct: bool, ip_address: str
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

    async def get_failed_attempts_count(self, user_id: UserIdType, ip_address: str) -> int:
        query = select(func.count()).select_from(LoginAttempt).where(
            LoginAttempt.user_id == user_id,
            LoginAttempt.is_correct.is_(False),
            LoginAttempt.created_at >= (datetime.datetime.now(datetime.UTC) - users_settings.LOGIN_CODE_EXPIRES_IN_TIMEDELTA),
            LoginAttempt.ip_address == ip_address,
        )
        return await self.session.scalar(query) or 0
