from typing import Annotated, Any

from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)

from modules.users.dependencies import get_access_token_db
from modules.users.models import AccessToken
from modules.users.models.access_token import ActiveAccessTokenDatabase
from modules.users.settings import users_settings


class TouchingDatabaseStrategy(DatabaseStrategy):
    """Extends DatabaseStrategy to update last_used_at after successful auth."""

    async def read_token(self, token: str | None, user_manager: Any) -> Any | None:
        user = await super().read_token(token, user_manager)
        if user is not None and token is not None and isinstance(self.database, ActiveAccessTokenDatabase):
            await self.database.touch_last_used(token)
        return user


def get_database_strategy(
    access_token_db: Annotated[AccessTokenDatabase[AccessToken], Depends(get_access_token_db)],
) -> TouchingDatabaseStrategy:
    return TouchingDatabaseStrategy(access_token_db, lifetime_seconds=users_settings.ACCESS_TOKEN_LIFETIME_SECONDS)


bearer_transport = BearerTransport(tokenUrl=users_settings.BEARER_TRANSPORT_TOKEN_URL)


auth_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
