from app.main import bp
from flask import render_template

@bp.route('/')
@bp.route('/dashboard')
def dashboard():
    return render_template('main/dashboard.html')