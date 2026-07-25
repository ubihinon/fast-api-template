from slowapi import Limiter
from slowapi.util import get_remote_address

from core.settings import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.CELERY_BROKER_URL,
)
