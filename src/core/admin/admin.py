from starlette_admin.contrib.sqla import Admin, ModelView
from db.session import engine
from models import User, AccessToken
from models.access_token import LoginToken


def setup_admin(app):
    admin = Admin(engine, title='FastAPI Template Admin')
    admin.mount_to(app)

    admin.add_view(ModelView(User))
    admin.add_view(ModelView(AccessToken))
    admin.add_view(ModelView(LoginToken))

    return admin
