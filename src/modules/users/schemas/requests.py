from fastapi_users import schemas
from pydantic import EmailStr


class LoginWithEmailRequestSchema(schemas.BaseModel):
    email: schemas.EmailStr


class VerifyLoginRequestSchema(schemas.BaseModel):
    email: EmailStr
    code: str
