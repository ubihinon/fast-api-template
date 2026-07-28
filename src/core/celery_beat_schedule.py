from datetime import timedelta

CELERY_BEAT_SCHEDULE = {
    "my-hourly-task": {
        "task": "notifications.hourly_test",
        "schedule": timedelta(hours=1),
    }
}
