from starlette_admin.contrib.sqla import Admin, ModelView

from core.database import engine
from modules.users.models import AccessToken, LoginToken, User


def setup_admin(app):
    admin = Admin(engine, title='FastAPI Template Admin')
    admin.mount_to(app)

    admin.add_view(ModelView(User))
    admin.add_view(ModelView(AccessToken))
    admin.add_view(ModelView(LoginToken))

    return admin
