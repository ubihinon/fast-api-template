from typing import Annotated

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from api.auth.user_manager import UserManager
from api.dependencies.auth.users import get_user_db


async def get_user_manager(user_db: Annotated[SQLAlchemyUserDatabase, Depends(get_user_db)]):
    yield UserManager(user_db)
