from fastapi import APIRouter

from api.dependencies.auth.backend import auth_backend
from api.dependencies.auth.fastapi_users import fastapi_users
from schemas.user import UserCreate, UserRead

router = APIRouter(prefix='/auth', tags=['Auth'])

# /login and /logout
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
)

# /register
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# /request-verify-token and /verify
router.include_router(fastapi_users.get_verify_router(UserRead))
