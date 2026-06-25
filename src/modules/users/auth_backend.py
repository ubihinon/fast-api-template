from typing import Annotated

from fastapi import Depends
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from modules.users.dependencies import get_access_token_db
from modules.users.models import AccessToken
from fastapi_users.authentication import AuthenticationBackend

from fastapi_users.authentication import BearerTransport

from core.settings import settings


def get_database_strategy(
    access_token_db: Annotated[AccessTokenDatabase[AccessToken], Depends(get_access_token_db)],
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=settings.ACCESS_TOKEN_LIFETIME_SECONDS)


bearer_transport = BearerTransport(tokenUrl=settings.BEARER_TRANSPORT_TOKEN_URL)


auth_backend = AuthenticationBackend(
    name="access-tokens-db",
    transport=bearer_transport,
    get_strategy=get_database_strategy,
)
