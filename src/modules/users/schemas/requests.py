from fastapi_users import schemas
from pydantic import EmailStr, Field


class LoginWithEmailRequestSchema(schemas.BaseModel):
    email: schemas.EmailStr


class VerifyLoginRequestSchema(schemas.BaseModel):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
