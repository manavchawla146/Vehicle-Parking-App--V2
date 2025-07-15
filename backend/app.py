from flask import Flask
from flask_cors import CORS
from database import db
from cache import cache
from celery_worker import make_celery

app = Flask(__name__)
app.config.from_pyfile('config.py')

CORS(app)
db.init_app(app)
cache.init_app(app)
celery = make_celery(app)

# Register Blueprints here
# from routes.admin import admin_bp
# from routes.user import user_bp
# app.register_blueprint(admin_bp)
# app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=True)
