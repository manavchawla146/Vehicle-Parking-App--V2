from celery_app import create_app, db
from celery_app import models  # noqa: F401
import jobs.scheduler  # Import scheduler to load beat_schedule configuration

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Optional: create tables if not exist
    app.config.from_pyfile('../config.py')
    app.run(debug=True)