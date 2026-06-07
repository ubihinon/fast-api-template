from fastapi_users import schemas


class LoginResponse(schemas.BaseModel):
    message: str


class LoginWithEmailRequestSchema(schemas.BaseModel):
    email: schemas.EmailStr
