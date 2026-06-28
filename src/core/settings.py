import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from sentry_sdk.integrations.fastapi import FastApiIntegration


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Template"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "error"
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
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    SENTRY_DSN: str | None = None
    SENTRY_INTEGRATIONS: list = [FastApiIntegration()]
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    SENTRY_PROFILE_SESSION_SAMPLE_RATE: float = 1.0

    GRAFANA_LOKI_URL: str = ""
    GRAFANA_API_USERNAME: str = ""
    GRAFANA_API_PASSWORD: str = ""


settings = Settings()
