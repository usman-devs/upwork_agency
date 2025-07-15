from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

class Config:
    # Security and Core Settings
    SECRET_KEY = os.getenv('SECRET_KEY', None)
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        f"sqlite:///{BASE_DIR / 'instance' / 'site.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine Options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300 if FLASK_ENV == 'development' else 3600,
        'pool_size': 10 if FLASK_ENV == 'development' else 20,
        'max_overflow': 20 if FLASK_ENV == 'development' else 30
    }

    # Session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
