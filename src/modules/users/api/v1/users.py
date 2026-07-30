from fastapi import APIRouter

from modules.users.dtos.user import UserRead, UserUpdate
from modules.users.fastapi_users_config import fastapi_users

router = APIRouter(prefix="/users", tags=["Users"])

# /me and /{id}
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
)
