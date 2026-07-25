import logging
from contextlib import asynccontextmanager

import sentry_sdk

from core.logger_setup import setup_logging
from core.settings import settings


from fastapi import FastAPI
from core import admin
from modules.users.api.v1 import router as users_router

logger = logging.getLogger(__name__)

# sentry_sdk.init(
#     dsn=settings.SENTRY_DSN,
#     environment=settings.ENVIRONMENT,
#     integrations=settings.SENTRY_INTEGRATIONS,
#     traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
#     profile_session_sample_rate=settings.SENTRY_PROFILE_SESSION_SAMPLE_RATE,
#     profile_lifecycle="trace",
# )

listener = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting FastAPI application...")

    if settings.GRAFANA_API_USERNAME is None or settings.GRAFANA_API_PASSWORD is None:
        logger.warning("GRAFANA_API_USERNAME or GRAFANA_API_PASSWORD not set!")
        logger.warning("Logs won't be sent in Grafana Loki")
    else:
        logger.info(f"✓ Grafana Loki URL: {settings.GRAFANA_LOKI_URL}")

    yield

    logger.info("🛑 Shutting down FastAPI application...")

    listener.stop()


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.include_router(users_router)


if settings.ENABLE_ADMIN:
    admin.setup_admin(app)
