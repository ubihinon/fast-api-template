from pathlib import Path
from typing import Optional
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict



class EmailSettings(BaseSettings):
    MAIL_USERNAME: str = "username@example.com"
    MAIL_PASSWORD: str = "<MAIL_PASSWORD>"
    MAIL_FROM: EmailStr = "username@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "FastAPI Application"

    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    TEMPLATE_FOLDER: Optional[Path] = Path(__file__).parent / "templates"
    # Disables sending emails for testing
    # SUPPRESS_SEND: bool = True
    SUPPRESS_SEND: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
