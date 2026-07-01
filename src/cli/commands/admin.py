import asyncio
import sys
from pathlib import Path

import typer
from sqlalchemy import select

from core.settings import settings

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.admin.models import UserAdmin
from core.admin.utils import hash_password
from core.database import async_session


admin_app = typer.Typer(help="Admin commands")


@admin_app.command(name="create-superuser")
def createsuperuser(
    username: str = typer.Option(None, prompt="Username", help="Username"),
    email: str = typer.Option(None, prompt="Email", help="Email"),
    password: str = typer.Option(None, prompt=True, hide_input=True, help="Password"),
    password_confirm: str = typer.Option(None, prompt=True, hide_input=True, help="Confirm password")
):
    try:
        asyncio.run(_createsuperuser(username, email, password, password_confirm))
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(code=1)


async def _createsuperuser(username: str, email: str, password: str, password_confirm: str):
    async with async_session() as session:
        try:
            query = select(UserAdmin).where(UserAdmin.username == username)
            result = await session.execute(query)
            existing_user_admin = result.scalar_one_or_none()
            if existing_user_admin:
                typer.echo(f"❌ User '{username}' already exists!", err=True)
                raise typer.Exit(code=1)

            if password != password_confirm:
                typer.echo("❌ Passwords do not match!", err=True)
                raise typer.Exit(code=1)

            if len(password) < settings.ADMIN_PASSWORD_MIN_LENGTH:
                typer.echo(
                    f"❌ Password must contain at least {settings.ADMIN_PASSWORD_MIN_LENGTH} symbols!", err=True
                )
                raise typer.Exit(code=1)

            admin_user = UserAdmin(
                username=username,
                email=email,
                password_hash=hash_password(password),
                full_name=username,
                is_active=True,
                is_superuser=True,
            )
            session.add(admin_user)
            await session.commit()
            typer.echo(f"✅ Superuser '{username}' created successfully!")
        except typer.Exit:
            await session.rollback()
            raise
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            await session.rollback()
            raise


@admin_app.command(name="delete-user")
def delete_user(
    email: str = typer.Option(None, prompt="Email", help="Email"),
):
    try:
        asyncio.run(_delete_user(email))
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ Unexpected error: {e}", err=True)
        raise typer.Exit(code=1)


async def _delete_user(email: str):
    async with async_session() as session:
        try:
            query = select(UserAdmin).where(
                UserAdmin.email == email,
            )
            result = await session.execute(query)
            user_admin = result.scalar_one_or_none()

            await session.delete(user_admin)
            await session.commit()

            typer.echo(f"✅ Deleted {email} user!")
        except typer.Exit:
            await session.rollback()
            raise
        except Exception as e:
            typer.echo(f"Error: {e}", err=True)
            await session.rollback()
            raise
