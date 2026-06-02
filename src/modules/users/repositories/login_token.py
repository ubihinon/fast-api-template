import datetime
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.types import UserIdType
from modules.users.models import AccessToken, LoginToken
from modules.users.schemas.access_token import AccessTokenSchema
from modules.users.schemas.login_token import LoginTokenSchema


class LoginTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def generate(self, user_id: UserIdType, expires_at: datetime.datetime) -> LoginTokenSchema:
        access_token = LoginToken(
            token=secrets.token_urlsafe(48),
            user_id=user_id,
            expires_at=expires_at,
        )
        self.session.add(access_token)
        await self.session.flush()
        return LoginTokenSchema.model_validate(access_token)

    async def get(self, token: str) -> LoginTokenSchema:
        query = select(LoginToken).where(
            LoginToken.token == token,
            LoginToken.is_active == True,
            LoginToken.expires_at > datetime.now(datetime.UTC)
        )
        result = await self.session.execute(query)
        login_token_record = result.scalar_one_or_none()

        if not login_token_record:
            raise ValueError("Token is invalid or expired")

        return LoginTokenSchema.model_validate(login_token_record)

    # query = (
    #     select(User).where(User.email == email)
    # )
    # result = await self.session.execute(query)
    # user = result.all()
    # return UserSchema.model_validate(user) if user else {}
