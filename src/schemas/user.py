import datetime

from fastapi_users import schemas

from types import UserIdType


class UserRead(schemas.BaseUser[UserIdType]):
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


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
