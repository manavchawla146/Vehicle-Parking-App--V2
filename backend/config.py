import os

# --------------------------
# Core Configuration
# --------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secret-key')  # Make this strong and hidden in production
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../instance/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# --------------------------
# Caching Configuration
# --------------------------
CACHE_TYPE = "redis"
CACHE_REDIS_URL = "redis://localhost:6379/1"  # Use different DB than Celery
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default
CACHE_KEY_PREFIX = "parking_app_"

# Cache timeouts for different types of data
CACHE_TIMEOUTS = {
    'lots': 300,        # 5 minutes for parking lots
    'users': 600,       # 10 minutes for user data
    'history': 120,     # 2 minutes for parking history
    'notifications': 60, # 1 minute for notifications
    'summary': 180,     # 3 minutes for summary data
    'search': 60,       # 1 minute for search results
}

# --------------------------
# Session Settings (Optional but Useful)
# --------------------------
SESSION_TYPE = 'filesystem'  # To store sessions server-side (safer than cookie-based)
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True  # Signs session cookie for added security
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript from accessing the cookie
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False  # For localhost

# --------------------------
# Admin Credentials (Optional)
# --------------------------
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@gmail.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
