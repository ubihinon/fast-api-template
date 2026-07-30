import datetime

from fastapi_users import schemas


class LoginResponse(schemas.BaseModel):
    message: str


class LoginAccessTokenResponseSchema(schemas.BaseModel):
    access_token: str


class SessionSchema(schemas.BaseModel):
    id: int
    created_at: datetime.datetime
    expires_at: datetime.datetime
    last_used_at: datetime.datetime | None
    ip_address: str | None

    model_config = {"from_attributes": True}


class LoginAttemptSchema(schemas.BaseModel):
    id: int
    created_at: datetime.datetime
    is_correct: bool
    ip_address: str | None
    user_agent: str | None

    model_config = {"from_attributes": True}


class LoginHistoryPageSchema(schemas.BaseModel):
    items: list[LoginAttemptSchema]
    next_cursor: int | None
