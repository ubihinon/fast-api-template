import datetime

from sqlalchemy import select, update, and_

from core.models.types import UserIdType
from modules.users.models import LoginCode
from modules.users.repositories.base import BaseRepository


class LoginCodeRepository(BaseRepository):
    async def create(self, user_id: UserIdType, code: str, expires_at: datetime.datetime) -> LoginCode:
        login_code = LoginCode(
            code=code,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(login_code)
        await self.session.flush()
        return login_code

    async def get_active_and_deactivate(self, code: str, user_id: UserIdType) -> LoginCode | None:
        """Atomically find an active, non-expired code and deactivate it in one query."""
        result = await self.session.execute(
            update(LoginCode)
            .where(
                and_(
                    LoginCode.code == code,
                    LoginCode.user_id == user_id,
                    LoginCode.is_active.is_(True),
                    LoginCode.expires_at > datetime.datetime.now(datetime.UTC),
                )
            )
            .values(is_active=False)
            .returning(LoginCode)
        )
        await self.session.flush()
        return result.scalar_one_or_none()

    async def deactivate_all_for_user(self, user_id: UserIdType) -> None:
        await self.session.execute(
            update(LoginCode)
            .where(LoginCode.user_id == user_id, LoginCode.is_active.is_(True))
            .values(is_active=False)
        )
        await self.session.flush()
