from fastapi import FastAPI
import admin
from api.v1 import router

app = FastAPI()

app.include_router(router)

admin.init_admin(app)
