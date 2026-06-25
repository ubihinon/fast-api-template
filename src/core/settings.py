import logging

from pydantic_settings import BaseSettings, SettingsConfigDict
from sentry_sdk.integrations.fastapi import FastApiIntegration

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Template"
    APP_VERSION: str = "1.0.0"

    ENABLE_ADMIN: bool = True
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@0.0.0.0:5432/postgres"

    BEARER_TRANSPORT_TOKEN_URL: str = "api/v1/auth/login"

    ACCESS_TOKEN_LIFETIME_SECONDS: int = 3600
    RESET_PASSWORD_TOKEN_SECRET: str = "<PASSWORD>"
    VERIFICATION_TOKEN_SECRET: str = "<PASSWORD>"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND_URL: str = "redis://localhost:6379/1"
    CELERY_ALWAYS_EAGER: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    SENTRY_DSN: str = None
    SENTRY_INTEGRATIONS: list = [FastApiIntegration()]
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    SENTRY_PROFILE_SESSION_SAMPLE_RATE: float = 1.0
    ENVIRONMENT: str = "development"

settings = Settings()
