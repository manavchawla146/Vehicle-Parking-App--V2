# backend/celery_app/celery_worker.py

from celery import Celery
from celery.schedules import crontab

celery = Celery(
    'celery_app',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=[
        'jobs.reminders',  #  This registers your task file
        'jobs.reports'
    ]
)

# 👇 Optional, or load from config file
celery.conf.beat_schedule = {
    'daily-reminder-task': {
        'task': 'jobs.reminders.send_reminder',
        'schedule': crontab(minute='*/1'),  # For testing every 1 min
    },
}
