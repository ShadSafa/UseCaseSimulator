"""
Configuration settings for the Use Case Simulator Web UI.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False

    # Session settings
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'data', 'sessions')
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # Upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data', 'uploads')

    # Game settings
    MAX_SIMULATION_ROUNDS = 15
    SESSION_TIMEOUT_MINUTES = 120

    # Analytics settings
    ENABLE_ANALYTICS = True
    CHART_CACHE_TIMEOUT = 300  # 5 minutes

    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SESSION_TYPE = 'filesystem'

    # Development-specific settings
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Use environment variables for production secrets
    SECRET_KEY = os.environ.get('USECASE_SECRET_KEY')

    # Production session settings
    SESSION_TYPE = 'filesystem'  # Could be upgraded to Redis in production
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

    # Use in-memory sessions for testing
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.getcwd(), 'data', 'test_sessions')


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class based on environment."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    return config.get(config_name, config['default'])


# Ensure required directories exist
def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        os.path.join(os.getcwd(), 'data', 'sessions'),
        os.path.join(os.getcwd(), 'data', 'uploads'),
        os.path.join(os.getcwd(), 'data', 'test_sessions'),
        os.path.join(os.getcwd(), 'web_ui', 'static', 'css'),
        os.path.join(os.getcwd(), 'web_ui', 'static', 'js'),
        os.path.join(os.getcwd(), 'web_ui', 'static', 'img'),
        os.path.join(os.getcwd(), 'web_ui', 'templates'),
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Call ensure_directories when this module is imported
ensure_directories()