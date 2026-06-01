from typing import Annotated

from fastapi import Depends
from fastapi_users.authentication.strategy.db import AccessTokenDatabase, DatabaseStrategy

from core.settings import ACCESS_TOKEN_LIFETIME_SECONDS
from modules.users.api.dependencies.auth.access_tokens import get_access_token_db
from modules.users.models import AccessToken


def get_database_strategy(
    access_token_db: Annotated[AccessTokenDatabase[AccessToken], Depends(get_access_token_db)],
) -> DatabaseStrategy:
    return DatabaseStrategy(access_token_db, lifetime_seconds=ACCESS_TOKEN_LIFETIME_SECONDS)
