import os
from dotenv import load_dotenv
from datetime import timedelta

# Get the root directory of the project
root_dir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv(os.path.join(root_dir, '.env'))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join(root_dir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask Core Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Database Configuration - Using absolute path
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        f'sqlite:///{os.path.join(root_dir, "instance", "site.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # ... rest of your config remains the same ...

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
        'pool_size': 20,
        'max_overflow': 30
    }

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}