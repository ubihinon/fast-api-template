from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    "my-hourly-task": {
        "task": "modules.notifications.tasks.hourly_test",
        "schedule": timedelta(hours=1),
    }
}
