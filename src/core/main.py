import sys

sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from fastapi import FastAPI
from core import admin
from modules.users.api.v1 import router as users_router
from core.settings import ENABLE_ADMIN

app = FastAPI()

app.include_router(users_router)


if ENABLE_ADMIN:
    admin.setup_admin(app)
