import sys

sys.path.insert(0, str(__file__).rsplit('/', 2)[0])
from commands import cli_app

# from src.cli.commands import cli_app

if __name__ == "__main__":
    cli_app()
