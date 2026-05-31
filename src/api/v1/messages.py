from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies.auth.fastapi_users import current_active_superuser, current_active_user
from models import User
from schemas.user import UserRead

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("")
async def get_messages(user: Annotated[User, Depends(current_active_user)]):
    return {
        "messages": ["m1", "m2", "m3"],
        "user": UserRead.model_validate(user),
    }


@router.get("/secrets")
async def get_superuser_messages(user: Annotated[User, Depends(current_active_superuser)]):
    return {
        "messages": ["secret-m1", "secret-m2", "secret-m3"],
        "user": UserRead.model_validate(user),
    }
