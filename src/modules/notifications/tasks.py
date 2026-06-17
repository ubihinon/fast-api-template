import logging

from core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="Test task")
def test(self):
    logger.info("TEST TASK!!!")


@celery_app.task(bind=True, name="Test task")
def hourly_test(self):
    logger.info("HOURLY TEST TASK!!!")
