import asyncio
import contextlib
import logging
import sys

import typer
from fastapi_users.exceptions import UserAlreadyExists

from . import cli_app

# from cli.commands import cli_app

# sys.path.insert(0, str(__file__).rsplit('/', 1)[0] + '/../')
# from src.cli.commands import cli_app
# from src.core.database import async_session
# from modules.users.api.auth.user_manager import UserManager
# from modules.users.api.dependencies.auth.user_manager import get_user_manager
# from modules.users.api.dependencies.auth.users import get_user_db
# from modules.users.models import User
# from modules.users.schemas.user import UserCreate


logger = logging.getLogger(__name__)

# get_user_db_context = contextlib.asynccontextmanager(get_user_db)
# get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


# @cli_app.command()
# async def create_user(user_manager: UserManager, user_create: UserCreate) -> User:
#     try:
#         user = await user_manager.create(user_create=user_create, safe=False)
#     except UserAlreadyExists:
#         typer.echo(f"Superuser {user_create.email} already exists")
#         # logger.error(f"User {user_create.email} already exists")
#         raise
#     return user


default_email = "admin@admin.com"
default_password = "123456"
default_is_active = True
default_is_superuser = True
default_is_verified = True


@cli_app.command(name='create-superuser')
def create_superuser(
    email: str = default_email,
    password: str = default_password,
    is_active: bool = default_is_active,
    is_superuser: bool = default_is_superuser,
    is_verified: bool = default_is_verified
):
    typer.echo(f"Superuser process")
    # user_create = UserCreate(
    #     email=email,
    #     password=password,
    #     is_active=is_active,
    #     is_superuser=is_superuser,
    #     is_verified=is_verified
    # )
    # async with async_session() as session:
    #     async with get_user_db_context(session) as user_db:
    #         async with get_user_manager_context(user_db) as user_manager:
    #             return await create_user(user_manager, user_create)

# if __name__ == "__main__":
#     cli_app()
