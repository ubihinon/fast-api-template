from fastapi import Request

from core.settings import settings


def get_client_ip(request: Request) -> str | None:
    if settings.TRUST_PROXY_HEADERS:
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
    if request.client is None:
        return None
    return request.client.host
