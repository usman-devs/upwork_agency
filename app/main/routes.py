from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, or_

from app import db  # Centralized db import
from app.models import Task, Project, User, Bid

# Blueprint named consistently with registration
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage with recent activity"""
    try:
        # recent_tasks = Task.query.order_by(Task.id.desc()).limit(5).all()
        # recent_projects = Project.query.order_by(Project.id.desc()).limit(5).all()
        
        # return render_template('main/index.html',
                            # tasks=recent_tasks,
                            # projects=recent_projects,
                            # todos=[])
    
        return render_template('main/index.html')
    except Exception as e:
        current_app.logger.error(f"Index error: {str(e)}", exc_info=True)
        flash('Error loading homepage', 'danger')
        return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Role-specific dashboard view"""
    try:
        # Initialize variables
        projects, tasks, team_members, metrics = [], [], [], {}
        
        if current_user.role == 'admin':
            projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
            tasks = Task.query.order_by(Task.created_at.desc()).limit(20).all()
            team_members = User.query.filter(User.role != 'admin').limit(5).all()
            
            metrics.update({
                'active_projects': db.session.query(Project)
                                    .filter_by(status='active').count(),
                'pending_bids': db.session.query(Bid)
                                 .filter_by(status='draft').count(),
                'revenue': db.session.query(func.sum(Project.budget))
                            .filter_by(status='active').scalar() or 0
            })

        elif current_user.role == 'manager':
            projects = Project.query.filter_by(manager_id=current_user.id)\
                          .order_by(Project.created_at.desc()).limit(5).all()
            project_ids = [p.id for p in projects]
            
            tasks = Task.query.filter(
                or_(
                    Task.project_id.in_(project_ids),
                    Task.assignee_id == current_user.id
                )
            ).order_by(Task.created_at.desc()).limit(20).all()
            
            team_members = User.query.filter_by(availability=True).limit(5).all()

        else:  # Regular member
            tasks = Task.query.filter_by(assignee_id=current_user.id)\
                     .order_by(Task.created_at.desc()).limit(20).all()
            projects = Project.query.join(Task)\
                          .filter(Task.assignee_id == current_user.id)\
                          .order_by(Project.created_at.desc()).limit(5).all()

        # Calculate statistics
        task_stats = {
            'total': len(tasks),
            'pending': sum(1 for t in tasks if t.status == 'todo'),
            'completed': sum(1 for t in tasks if t.status == 'completed'),
            'overdue': sum(1 for t in tasks if t.deadline and 
                         t.deadline < datetime.utcnow() and 
                         t.status != 'completed')
        }

        # Get upcoming deadlines
        upcoming_tasks = sorted(
            [t for t in tasks if t.deadline and t.deadline >= datetime.utcnow()],
            key=lambda x: x.deadline
        )[:5]

        return render_template('main/dashboard.html',
                            projects=projects,
                            recent_tasks=tasks[:5],
                            upcoming_tasks=upcoming_tasks,
                            team_members=team_members,
                            metrics=metrics,
                            stats=task_stats,
                            now=datetime.utcnow())

    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        flash('Error loading dashboard data', 'danger')
        return redirect(url_for('main.index'))