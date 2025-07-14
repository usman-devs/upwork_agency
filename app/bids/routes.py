from flask import Blueprint

bp = Blueprint('bids', __name__)

@bp.route('/')
def index():
    return "Bids overview"  # Placeholder for now

@bp.route('/<int:bid_id>')
def view(bid_id):
    return f"Viewing bid {bid_id}"  # Placeholder for now