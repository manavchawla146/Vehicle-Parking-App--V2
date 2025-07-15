import os

# --------------------------
# Core Configuration
# --------------------------
SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secret-key')  # Make this strong and hidden in production
SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../instance/app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# --------------------------
# Session Settings (Optional but Useful)
# --------------------------
SESSION_TYPE = 'filesystem'  # To store sessions server-side (safer than cookie-based)
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True  # Signs session cookie for added security
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript from accessing the cookie
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False  # Set to True in production over HTTPS

# --------------------------
# Admin Credentials (Optional)
# --------------------------
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@gmail.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
