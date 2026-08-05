import logging
import warnings
from contextlib import asynccontextmanager

warnings.filterwarnings("ignore", message=".*HTTP_422_UNPROCESSABLE_ENTITY.*", module="starlette_admin.*")

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from sentry_sdk.integrations.fastapi import FastApiIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from core import admin
from core.i18n import load_translations
from core.limiter import limiter
from core.logger_setup import setup_logging
from core.middleware import LanguageMiddleware
from core.settings import settings
from modules.notifications.template_renderer import _get_env
from modules.users.api.v1 import router as users_router

logger = logging.getLogger(__name__)

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[FastApiIntegration()],
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profile_session_sample_rate=settings.SENTRY_PROFILE_SESSION_SAMPLE_RATE,
        profile_lifecycle="trace",
    )

listener = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_translations()
    for lang in _translations:
        _get_env(lang)
    logger.info("🚀 Starting FastAPI application...")

    if settings.GRAFANA_API_USERNAME == "" or settings.GRAFANA_API_PASSWORD == "":
        logger.warning("GRAFANA_API_USERNAME or GRAFANA_API_PASSWORD not set!")
        logger.warning("Logs won't be sent in Grafana Loki")
    else:
        logger.info(f"✓ Grafana Loki URL: {settings.GRAFANA_LOKI_URL}")

    yield

    logger.info("🛑 Shutting down FastAPI application...")

    listener.stop()


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)  # type: ignore[arg-type]
app.add_middleware(LanguageMiddleware)
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)


if settings.ENABLE_ADMIN:
    admin.setup_admin(app)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
        }
    }
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            if "security" not in operation:
                operation["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore[method-assign]
