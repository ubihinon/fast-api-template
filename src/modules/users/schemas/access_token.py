from fastapi_users import schemas
from pydantic import ConfigDict


class AccessTokenSchema(schemas.BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
