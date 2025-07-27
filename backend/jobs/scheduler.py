from celery.schedules import crontab
from celery_app import celery
from jobs.reminders import send_reminder

celery.conf.beat_schedule = {
    'daily-reminder-task': {
        'task': 'jobs.reminders.send_reminder',
        'schedule': crontab(hour=14, minute=32)  # 12:08 PM daily
       # 'schedule': crontab(minute='*/1'),  # Every minute for testing
    },
}
