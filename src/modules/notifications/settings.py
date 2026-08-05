import os
from pathlib import Path

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EmailSettings(BaseSettings):
    MAIL_USERNAME: str = "username@example.com"
    MAIL_PASSWORD: SecretStr = SecretStr("<MAIL_PASSWORD>")
    MAIL_FROM: EmailStr = "username@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "FastAPI Application"

    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    TEMPLATE_FOLDER: Path | None = Path(__file__).parent / "templates"
    # Disables sending emails for testing
    SUPPRESS_SEND: bool = False

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


email_settings = EmailSettings()
