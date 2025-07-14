from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_htmx import HTMX
from flask_bcrypt import Bcrypt
from config import Config

# Initialize extensions outside create_app
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bootstrap = Bootstrap()
htmx = HTMX()
bcrypt = Bcrypt()

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    htmx.init_app(app)
    bcrypt.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.auth.routes import bp as auth_bp
    from app.main.routes import bp as main_bp
    from app.projects.routes import bp as projects_bp
    from app.tasks.routes import bp as tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)

    return app  # Single app object returned