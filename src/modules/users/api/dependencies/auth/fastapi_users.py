from fastapi_users import FastAPIUsers

from core.models.types import UserIdType
from modules.users.api.dependencies.auth.backend import auth_backend
from modules.users.api.dependencies.auth.user_manager import get_user_manager
from modules.users.models import User

fastapi_users = FastAPIUsers[User, UserIdType](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
