from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin import DropDown
from starlette_admin.contrib.sqla import Admin, ModelView

from core.admin.auth_provider import DatabaseAuthProvider
from core.database import engine
from core.settings import settings
from core.admin.models import UserAdmin
from modules.users.models import AccessToken, LoginAttempt, LoginCode, User


def setup_admin(app):
    admin = Admin(
        engine,
        title=f"{settings.APP_NAME} Admin",
        auth_provider=DatabaseAuthProvider(),
        middlewares=[
            Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY),
        ],
    )
    admin.mount_to(app)


    admin.add_view(
        DropDown(
            "Users",
            views=[
                ModelView(User),
                ModelView(AccessToken),
                ModelView(LoginCode),
                ModelView(LoginAttempt),
            ],
        )
    )

    admin.add_view(
        DropDown(
            "Admin",
            views=[
                ModelView(UserAdmin),
            ],
        )
    )

    return admin
