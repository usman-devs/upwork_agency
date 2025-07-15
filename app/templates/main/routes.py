from flask_login import login_required
from app.main import bp
from flask import render_template

@bp.route('/')
@bp.route('/dashboard')
def dashboard():
    return render_template('main/dashboard.html')

@bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    from app import db
    from app.models import Project
    project = Project.query.get_or_404(project_id)
    return render_template('main/details.html', project=project, title='Project Details')
