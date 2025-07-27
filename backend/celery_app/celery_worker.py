# backend/celery_app/celery_worker.py

from celery import Celery
from celery.schedules import crontab

celery = Celery(
    'celery_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=[
        'jobs.reminders',
        'jobs.reports'
    ]
)

celery.conf.beat_schedule = {
    'daily-reminder-task': {
        'task': 'jobs.reminders.send_reminder',  # Just prints log
        'schedule': crontab(hour=22, minute=10),  # 10:10 PM
    },
}
