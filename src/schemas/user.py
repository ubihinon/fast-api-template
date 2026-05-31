import datetime

from fastapi_users import schemas
from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate
from pydantic import ConfigDict

from app_types.user_id import UserIdType


class LoginResponse(schemas.BaseModel):
    """Ответ на запрос входа."""
    message: str


class VerifyLoginResponse(schemas.BaseModel):
    """Ответ на верификацию входа."""
    access_token: str
    token_type: str = "bearer"


class UserCreateMagicLink(schemas.BaseModel):
    email: schemas.EmailStr


class UserRead(schemas.BaseUser[UserIdType]):
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserCreate(BaseUserCreate):
    model_config = ConfigDict(
        from_attributes=True,
    )


class UserUpdate(BaseUserUpdate):
    model_config = ConfigDict(
        from_attributes=True,
    )


# from pydantic import BaseModel, EmailStr
#
#
# class UserSchema(BaseModel):
#     id: int
#     email: EmailStr
#     name: str
#     is_active: bool
#
#     class Config:
#         from_attributes = True
