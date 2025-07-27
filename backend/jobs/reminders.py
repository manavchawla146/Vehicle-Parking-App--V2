# backend/jobs/reminders.py

from celery_app import celery
from datetime import datetime
from celery.utils.log import get_task_logger

# Set up logger
logger = get_task_logger(__name__)

@celery.task(name='jobs.reminders.send_reminder')
def send_reminder():
    logger.info(f"✅ Reminder sent at {datetime.now()}")
    return f"Hello Reminder sent at {datetime.now()}"
