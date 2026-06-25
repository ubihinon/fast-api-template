import sys

import sentry_sdk

from core.settings import settings

sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from fastapi import FastAPI
from core import admin
from modules.users.api.v1 import router as users_router

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    integrations=settings.SENTRY_INTEGRATIONS,
    traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
    profile_session_sample_rate=settings.SENTRY_PROFILE_SESSION_SAMPLE_RATE,
    profile_lifecycle="trace",
)

app = FastAPI()

app.include_router(users_router)


if settings.ENABLE_ADMIN:
    admin.setup_admin(app)
