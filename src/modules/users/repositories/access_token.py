import datetime
from typing import cast

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult

from core.models.types import UserIdType
from modules.users.models import AccessToken
from modules.users.repositories.base import BaseRepository


class AccessTokenRepository(BaseRepository):
    async def create(
        self, token: str, user_id: UserIdType, expires_at: datetime.datetime, ip_address: str | None = None
    ) -> AccessToken:
        access_token = AccessToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            ip_address=ip_address,
        )
        self.session.add(access_token)
        await self.session.flush()
        return access_token

    async def deactivate_token(self, user_id: UserIdType, token: str) -> bool:
        result = cast(CursorResult, await self.session.execute(
            update(AccessToken)
            .where(
                AccessToken.token == token,
                AccessToken.user_id == user_id
            )
            .values(is_active=False)
        ))
        await self.session.flush()
        return result.rowcount > 0

    async def get_active_sessions(self, user_id: UserIdType) -> list[AccessToken]:
        now = datetime.datetime.now(datetime.UTC)
        result = await self.session.execute(
            select(AccessToken)
            .where(
                AccessToken.user_id == user_id,
                AccessToken.is_active.is_(True),
                AccessToken.expires_at > now,
            )
            .order_by(AccessToken.created_at.desc())
        )
        return list(result.scalars().all())

    async def deactivate_all_tokens(self, user_id: UserIdType) -> bool:
        result = cast(CursorResult, await self.session.execute(
            update(AccessToken)
            .where(
                AccessToken.user_id == user_id,
                AccessToken.is_active.is_(True)
            )
            .values(is_active=False)
        ))
        await self.session.flush()
        return result.rowcount > 0
