from celery import Celery

from core.celery_beat_schedule import CELERY_BEAT_SCHEDULE
from core.settings import settings

celery_app = Celery(
    "fastapi_celery_app",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes hard limit
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    task_always_eager=settings.CELERY_ALWAYS_EAGER
)

# Auto-discover tasks from all registered apps
celery_app.autodiscover_tasks(["core.tasks", "modules.notifications"])

# Configure Celery Beat schedule for periodic tasks

celery_app.conf.beat_schedule = CELERY_BEAT_SCHEDULE
