from app.projects import bp  # Import the blueprint
from flask import render_template

@bp.route('/projects')
def projects_list():
    return render_template('projects/list.html')