from flask import Blueprint

bp = Blueprint('auth', __name__)  # Create blueprint once

from app.auth import routes  # Import routes AFTER creating the blueprint