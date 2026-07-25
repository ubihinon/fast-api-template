import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.dtos.auth import AccessTokenSchema
from modules.users.models import AccessToken
from modules.users.repositories.base import BaseRepository


class AccessTokenRepository(BaseRepository):
    async def create(self, token: str, user_id: UserIdType, expires_at: datetime.datetime) -> AccessTokenSchema:
        access_token = AccessToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(access_token)
        await self.session.flush()
        return AccessTokenSchema.model_validate(access_token)

    async def deactivate_token(self, user_id: UserIdType, token: str) -> bool:
        result = await self.session.execute(
            update(AccessToken)
            .where(
                AccessToken.token == token,
                AccessToken.user_id == user_id
            )
            .values(is_active=False)
        )
        await self.session.flush()
        return result.rowcount > 0

    async def deactivate_all_tokens(self, user_id: UserIdType) -> bool:
        result = await self.session.execute(
            update(AccessToken)
            .where(
                AccessToken.user_id == user_id,
                AccessToken.is_active.is_(True)
            )
            .values(is_active=False)
        )
        await self.session.flush()
        return result.rowcount > 0
