import datetime

from fastapi_users import schemas
from fastapi_users.schemas import BaseUserCreate, BaseUserUpdate
from pydantic import ConfigDict

from core.models.types import UserIdType


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
