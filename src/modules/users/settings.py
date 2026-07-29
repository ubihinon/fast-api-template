import datetime
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class UsersSettings(BaseSettings):
    BEARER_TRANSPORT_TOKEN_URL: str = "api/v1/auth/magic/login"

    ACCESS_TOKEN_LIFETIME_SECONDS: int = 3600
    RESET_PASSWORD_TOKEN_SECRET: str = Field(min_length=32)
    VERIFICATION_TOKEN_SECRET: str = Field(min_length=32)

    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_VERIFY: str = "10/minute"

    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_CODE_EXPIRES_IN_TIMEDELTA: datetime.timedelta = datetime.timedelta(minutes=15)

    @property
    def ACCESS_TOKEN_EXPIRES_IN_TIMEDELTA(self) -> datetime.timedelta:
        return datetime.timedelta(seconds=self.ACCESS_TOKEN_LIFETIME_SECONDS)

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


users_settings = UsersSettings()  # type: ignore[call-arg]
