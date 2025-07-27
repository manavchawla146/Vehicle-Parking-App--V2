# celery_worker.py

from celery import Celery
from celery.schedules import crontab

celery = Celery(
    'celery_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['jobs.reminders', 'jobs.reports']  # Task discovery
)

# Load config if any
celery.conf.timezone = 'Asia/Kolkata'

celery.conf.beat_schedule = {
    'daily-reminder-task': {
        'task': 'jobs.reminders.send_reminder',  # Send emails with PDF reports
        'schedule': crontab(hour=2, minute=40),  # 2:40 AM
    },
}
