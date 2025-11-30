from fastapi_users import FastAPIUsers

from api.dependencies.backend import auth_backend
from api.dependencies.user_manager import get_user_manager
from api.types.user_id import UserIdType
from models import User

fastapi_users = FastAPIUsers[User, UserIdType](
    get_user_manager,
    [auth_backend],
)
