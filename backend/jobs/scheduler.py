# backend/jobs/scheduler.py

from celery.schedules import crontab
from celery_app import celery
from jobs.reminders import send_reminder
from jobs.reports import generate_monthly_report  # Optional if using this task too

# Note: Schedule configuration is now in celery_worker.py to avoid circular imports
# This file is kept for reference but not actively used for scheduling
