from starlette_admin.contrib.sqla import Admin, ModelView
from db.session import engine
from models import User, AccessToken
from models.access_token import LoginToken


def init_admin(app):
    admin = Admin(engine, title='Example: SQLAlchemy')

    admin.add_view(ModelView(User))
    admin.add_view(ModelView(AccessToken))
    admin.add_view(ModelView(LoginToken))
    admin.mount_to(app)
