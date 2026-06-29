# import asyncio
# import contextlib
# import logging
# import sys
#
# import typer
# from fastapi_users.exceptions import UserAlreadyExists
#
# from . import cli_app
#
# # from cli.commands import cli_app
#
# # sys.path.insert(0, str(__file__).rsplit('/', 1)[0] + '/../')
# # from src.cli.commands import cli_app
# # from src.core.database import async_session
# # from modules.users.api.auth.user_manager import UserManager
# # from modules.users.api.dependencies.auth.user_manager import get_user_manager
# # from modules.users.api.dependencies.auth.users import get_user_db
# # from modules.users.models import User
# # from modules.users.schemas.user import UserCreate
#
#
# logger = logging.getLogger(__name__)
#
# # get_user_db_context = contextlib.asynccontextmanager(get_user_db)
# # get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)
#
#
# # @cli_app.command()
# # async def create_user(user_manager: UserManager, user_create: UserCreate) -> User:
# #     try:
# #         user = await user_manager.create(user_create=user_create, safe=False)
# #     except UserAlreadyExists:
# #         typer.echo(f"Superuser {user_create.email} already exists")
# #         # logger.error(f"User {user_create.email} already exists")
# #         raise
# #     return user
#
#
# default_email = "admin@admin.com"
# default_password = "123456"
# default_is_active = True
# default_is_superuser = True
# default_is_verified = True
#
#
# @cli_app.command(name="create-superuser")
# def create_superuser(
#     email: str = default_email,
#     password: str = default_password,
#     is_active: bool = default_is_active,
#     is_superuser: bool = default_is_superuser,
#     is_verified: bool = default_is_verified
# ):
#     typer.echo(f"Superuser process")
#     # user_create = UserCreate(
#     #     email=email,
#     #     password=password,
#     #     is_active=is_active,
#     #     is_superuser=is_superuser,
#     #     is_verified=is_verified
#     # )
#     # async with async_session() as session:
#     #     async with get_user_db_context(session) as user_db:
#     #         async with get_user_manager_context(user_db) as user_manager:
#     #             return await create_user(user_manager, user_create)
#
# # if __name__ == "__main__":
# #     cli_app()
import sys
from pathlib import Path

import typer
project_root = Path(__file__).parent.parent.parent.parent
print(f"ROOT_DIR: {project_root}")
sys.path.insert(0, str(project_root / "src"))

from core.admin.models import UserAdmin
from core.admin.utils import hash_password
from core.database import async_session, engine

app = typer.Typer(help="Управление приложением FastAPI")


def get_db():
    from sqlalchemy.orm import sessionmaker
    # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = async_session()
    try:
        return session
    finally:
        session.close()


@app.command()
def createsuperuser(
    username: str = typer.Option(..., prompt="Username", help="Имя пользователя"),
    email: str = typer.Option(..., prompt="Email", help="Email пользователя"),
    password: str = typer.Option(..., prompt=True, hide_input=True, help="Пароль"),
    password_confirm: str = typer.Option(..., prompt=True, hide_input=True, help="Подтверждение пароля"),
):
    if password != password_confirm:
        typer.echo("❌ Пароли не совпадают!", err=True)
        raise typer.Exit(code=1)

    if len(password) < 8:
        typer.echo("❌ Пароль должен содержать минимум 8 символов!", err=True)
        raise typer.Exit(code=1)

    db = get_db()

    admin_user = UserAdmin(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=username,
        is_active=True,
        is_superuser=True,
    )
    db.add(admin_user)

    db.flush()
    # db.refresh(admin_user)

    # Проверка существования пользователя
    # existing_user = db.query(User).filter(User.username == username).first()
    # if existing_user:
    #     typer.echo(f"❌ Пользователь '{username}' уже существует!", err=True)
    #     raise typer.Exit(code=1)

    # Создание пользователя
    # hashed_password = hash_password(password)
    # new_user = User(
    #     username=username,
    #     email=email,
    #     password=hashed_password,
    #     is_superuser=True,
    #     is_active=True
    # )

    # db.add(new_user)
    # db.commit()
    # db.refresh(new_user)

    typer.echo(f"✅ Суперпользователь '{username}' успешно создан!")


# @app.command()
# def list_users():
#     """Список всех пользователей."""
#     db = get_db()
#     users = db.query(User).all()
#
#     if not users:
#         typer.echo("Пользователей не найдено.")
#         return
#
#     typer.echo("\n📋 Список пользователей:")
#     typer.echo("-" * 60)
#     for user in users:
#         role = "👑 SUPERUSER" if user.is_superuser else "👤 USER"
#         status = "✅ Active" if user.is_active else "❌ Inactive"
#         typer.echo(f"{user.username:20} | {user.email:30} | {role:15} | {status}")
#     typer.echo("-" * 60)
#
#
# @app.command()
# def delete_user(username: str = typer.Argument(..., help="Имя пользователя для удаления")):
#     """Удалить пользователя."""
#     db = get_db()
#     user = db.query(User).filter(User.username == username).first()
#
#     if not user:
#         typer.echo(f"❌ Пользователь '{username}' не найден!", err=True)
#         raise typer.Exit(code=1)
#
#     # Подтверждение
#     if not typer.confirm(f"Вы уверены, что хотите удалить пользователя '{username}'?"):
#         typer.echo("Отменено.")
#         return
#
#     db.delete(user)
#     db.commit()
#     typer.echo(f"✅ Пользователь '{username}' удален!")


if __name__ == "__main__":
    app()
