from flask import Flask
from app.models import db
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from .models import User
from urllib.parse import quote_plus
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', None)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', None)

# Original password
raw_password = os.environ.get('DB_PASSWORD', None)
encoded_password = quote_plus(raw_password)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:{encoded_password}@localhost/upwork_agency"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app.config.from_pyfile('../.env', silent=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_email):
        return User.query.get(user_email)

    # Configure Flask-Login
    login_manager.login_view = 'auth_bp.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # Import models within app context to avoid circular imports
    with app.app_context():
        from app import models

    return app