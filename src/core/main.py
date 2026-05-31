from fastapi import FastAPI
from core import admin
from api.v1 import router
from core.settings import ENABLE_ADMIN

app = FastAPI()

app.include_router(router)

if ENABLE_ADMIN:
    admin.setup_admin(app)
