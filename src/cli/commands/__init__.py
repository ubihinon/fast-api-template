import typer

cli_app = typer.Typer()

__all__ = ["cli_app"]


from .create_superuser import create_superuser
