import datetime

from fastapi_users import schemas
from pydantic import ConfigDict

from core.models.types import UserIdType


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
