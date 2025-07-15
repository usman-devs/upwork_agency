from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Configure Flask-Login redirect view
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message_category = 'info'

    # Import blueprints only AFTER extensions are initialized
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # Import models AFTER db.init_app(app) to avoid circular import
    with app.app_context():
        from app import models

    return app
