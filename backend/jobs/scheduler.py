from celery.schedules import crontab
from celery_app import celery
from jobs.reminders import send_reminder

celery.conf.beat_schedule = {
    'daily-reminder-task': {
        'task': 'jobs.reminders.send_reminder',
        'schedule': crontab(hour=12, minute=00),  # 5:47 AM daily
    },
}
