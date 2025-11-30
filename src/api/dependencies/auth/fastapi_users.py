from fastapi_users import FastAPIUsers

from api.dependencies.auth.backend import auth_backend
from api.dependencies.auth.user_manager import get_user_manager
from types import UserIdType
from models import User

fastapi_users = FastAPIUsers[User, UserIdType](
    get_user_manager,
    [auth_backend],
)
