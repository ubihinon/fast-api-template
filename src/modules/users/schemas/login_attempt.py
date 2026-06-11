import datetime

from fastapi_users import schemas
from pydantic import ConfigDict, EmailStr

from core.models.types import UserIdType


class LoginAttemptReadSchema(schemas.BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    user_id: UserIdType
    email: EmailStr
    code_entered: str
    is_correct: bool
    ip_address: int
    created_at: datetime.datetime
