from celery_app import celery

@celery.task
def generate_monthly_report():
    # heavy logic to query DB, format and save/export
    print("📊 Report generated!")
