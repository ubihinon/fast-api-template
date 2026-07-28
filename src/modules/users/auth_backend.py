from typing import Annotated

from fastapi import Depends
from fastapi_users.authentication import AuthenticationBackend, BearerTransport
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)

from modules.users.dependencies import get_access_token_db
from modules.users.settings import users_settings
from modules.users.models import AccessToken


def get_database_strategy(
    access_token_db: Annotated[AccessTokenDatabase[AccessToken], Depends(get_access_token_db)],
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=users_settings.ACCESS_TOKEN_LIFETIME_SECONDS)


bearer_transport = BearerTransport(tokenUrl=users_settings.BEARER_TRANSPORT_TOKEN_URL)


auth_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
