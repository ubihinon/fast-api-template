from fastapi_users import schemas


class LoginResponse(schemas.BaseModel):
    message: str


class LoginAccessTokenResponseSchema(schemas.BaseModel):
    access_token: str
