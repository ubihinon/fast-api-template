from fastapi import APIRouter

from api.dependencies.auth.backend import auth_backend
from api.dependencies.auth.fastapi_users import fastapi_users

router = APIRouter(prefix='/auth', tags=['Auth'])

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)
