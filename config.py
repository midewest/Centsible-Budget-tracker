"""Configuration classes for Centsible Budget Tracker."""
import os
from datetime import timedelta

class Config:
    """Base configuration."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = os.environ.get('CSRF_SESSION_KEY') or 'dev-csrf-key'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 
                                  'instance', 'centsible.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=31)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """Production configuration."""
    # Override with environment variables in production
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}