import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration with PostgreSQL URL handling
    database_url = os.environ.get('DATABASE_URL') or 'sqlite:///tasktracker_pro.db'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'on']
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Upload settings
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # External integrations
    GOOGLE_CALENDAR_CREDENTIALS = os.environ.get('GOOGLE_CALENDAR_CREDENTIALS')
    SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

class ProductionConfig(Config):
    DEBUG = False
    
class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Redis for real-time features (optional)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
