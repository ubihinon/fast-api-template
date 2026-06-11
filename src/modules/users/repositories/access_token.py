import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import AccessToken
from modules.users.schemas.access_token import AccessTokenSchema


class AccessTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate(self, token: str, user_id: UserIdType, expires_at: datetime.datetime) -> AccessTokenSchema:
        access_token = AccessToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(access_token)
        await self.session.flush()
        return AccessTokenSchema.model_validate(access_token)
