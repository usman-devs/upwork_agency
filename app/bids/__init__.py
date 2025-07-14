# Initialize bids package
from .routes import bp

__all__ = ['bp']

from flask import Blueprint
bp = Blueprint('bids', __name__)

def register_blueprints(app):
    """Register all application blueprints"""
    from app.auth.routes import bp as auth_bp
    from app.main.routes import bp as main_bp
    from app.projects.routes import bp as projects_bp
    from app.tasks.routes import bp as tasks_bp
    from app.bids.routes import bp as bids_bp  # Now properly imported
    # from app.dashboard.routes import bp as dashboard_bp  # Removed due to unresolved import

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(bids_bp, url_prefix='/bids')  # Now registered
    # app.register_blueprint(dashboard_bp, url_prefix='/dashboard')  # Removed due to unresolved import