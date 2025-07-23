# backend/celery_app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py')
    CORS(app, supports_credentials=True)
    db.init_app(app)
    migrate.init_app(app, db)
    from .auth import auth_bp
    app.register_blueprint(auth_bp)
    from .user import user_bp
    app.register_blueprint(user_bp)
    from .admin import admin_bp
    app.register_blueprint(admin_bp)
    return app
from celery import Celery

celery = Celery(__name__, broker='redis://localhost:6379/0')

def make_celery(app):
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
