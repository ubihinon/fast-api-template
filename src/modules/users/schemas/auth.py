from fastapi_users import schemas


class LoginResponse(schemas.BaseModel):
    message: str


class VerifyLoginResponse(schemas.BaseModel):
    """Ответ на верификацию входа."""
    access_token: str
    token_type: str = "bearer"


class UserCreateMagicLink(schemas.BaseModel):
    email: schemas.EmailStr
