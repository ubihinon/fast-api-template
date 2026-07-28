from fastapi import Request
from slowapi import Limiter

from core.settings import settings


def get_client_ip_for_limiter(request: Request) -> str:
    if settings.TRUST_PROXY_HEADERS:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
    if request.client is None:
        return ""
    return request.client.host


limiter = Limiter(
    key_func=get_client_ip_for_limiter,
    storage_uri=settings.CELERY_BROKER_URL,
)
