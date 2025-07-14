from flask import Blueprint

# This file makes Python treat the directory as a package
from .routes import bp

bp = Blueprint('auth', __name__)  # Create blueprint once

from app.auth import routes  # Import routes AFTER creating the blueprint