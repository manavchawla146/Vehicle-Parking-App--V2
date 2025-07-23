from celery_app.celery_worker import celery
from datetime import datetime

@celery.task(name='jobs.reminders.send_reminder')
def send_reminder():
    print(f"✅ Reminder sent at {datetime.now()}")
