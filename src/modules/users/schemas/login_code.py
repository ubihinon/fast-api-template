import datetime

from fastapi_users import schemas
from pydantic import BaseModel, ConfigDict, EmailStr

from core.models.types import UserIdType


class LoginCodeReadSchema(schemas.BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    code: str
    user_id: UserIdType
    created_at: datetime.datetime
    expires_at: datetime.datetime
    is_active: bool
    attempts: int


class LoginWithEmailRequestSchema(schemas.BaseModel):
    email: EmailStr


class VerifyLoginRequestSchema(schemas.BaseModel):
    email: EmailStr
    code: str


class LoginResponseSchema(schemas.BaseModel):
    message: str
