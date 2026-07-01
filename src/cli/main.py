import typer

from .commands import admin_app

cli_app = typer.Typer(help="FastAPI Template CLI")

cli_app.add_typer(admin_app, name="admin")

if __name__ == "__main__":
    cli_app()
