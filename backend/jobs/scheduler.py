# backend/jobs/scheduler.py

from celery.schedules import crontab
from celery_app import celery
from jobs.reminders import send_reminder
from jobs.reports import generate_monthly_report  # Optional if using this task too

celery.conf.beat_schedule = {
    'daily-reminder-task': {
        'task': 'jobs.reminders.send_reminder',
        'schedule': crontab(hour=1, minute=10),  # 12:59 AM
        'options': {
            'expires': 60  # Optional: auto-expire after 1 min if not picked up
        }
    },

    # Optional: Uncomment if testing reports task too
    # 'monthly-report-task': {
    #     'task': 'jobs.reports.generate_monthly_report',
    #     'schedule': crontab(minute='*/2'),  # Every 2 mins for testing
    #     'options': {
    #         'expires': 120
    #     }
    # },
}
