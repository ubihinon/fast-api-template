from fastapi_users import schemas
from pydantic import ConfigDict


class LoginTokenSchema(schemas.BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
