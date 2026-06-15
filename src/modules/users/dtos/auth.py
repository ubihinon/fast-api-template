import datetime

from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr

from core.models.types import UserIdType


class LoginCodeReadSchema(schemas.BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    code: str
    user_id: UserIdType
    created_at: datetime.datetime
    expires_at: datetime.datetime
    is_active: bool

    def is_expired(self) -> bool:
        return self.expires_at <= datetime.datetime.now(datetime.UTC)


class LoginAttemptReadSchema(schemas.BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UserIdType
    email: EmailStr
    code_entered: str
    is_correct: bool
    ip_address: str
    created_at: datetime.datetime


class AccessTokenSchema(schemas.BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    token: str
    user_id: UserIdType
    created_at: datetime.datetime
    expires_at: datetime.datetime
    is_active: bool
