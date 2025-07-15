from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import func, or_

from app.models import Task, Project, Notification, User, Bid
from app.utils.helpers import calculate_feasibility

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    """Home page route"""
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    from app import db  # 🔥 FIX: avoid circular import by importing locally

    """Main dashboard with role-specific views"""
    try:
        # Base queries
        projects_query = Project.query
        tasks_query = Task.query

        if current_user.role == 'admin':
            projects = projects_query.order_by(Project.created_at.desc()).limit(5).all()
            tasks = tasks_query.order_by(Task.created_at.desc()).limit(20).all()
            team_members = User.query.filter(User.role != 'admin').limit(5).all()

            metrics = {
                'active_projects': projects_query.filter_by(status='active').count(),
                'pending_bids': Bid.query.filter_by(status='draft').count(),
                'revenue': db.session.query(func.sum(Project.budget)).filter_by(status='active').scalar() or 0,
            }

        elif current_user.role == 'manager':
            projects = projects_query.order_by(Project.created_at.desc()).limit(5).all()
            tasks = tasks_query.filter(
                or_(
                    Task.project_id.in_([p.id for p in projects]),
                    Task.assignee_id == current_user.id
                )
            ).order_by(Task.created_at.desc()).limit(20).all()
            team_members = User.query.filter_by(availability=True).limit(5).all()
            metrics = {}

        else:  # member
            projects = projects_query.join(Task).filter(
                Task.assignee_id == current_user.id
            ).order_by(Project.created_at.desc()).limit(5).all()
            tasks = tasks_query.filter_by(assignee_id=current_user.id).order_by(
                Task.created_at.desc()).limit(20).all()
            team_members = []
            metrics = {}

        # Calculated stats for dashboard
        total_projects = Project.query.count()
        total_tasks = len(tasks)
        pending_tasks = sum(1 for t in tasks if t.status == 'todo')
        completed_tasks = sum(1 for t in tasks if t.status == 'completed')
        recent_tasks = tasks[:5]

        upcoming_tasks = sorted(
            [t for t in tasks if t.deadline and t.deadline >= datetime.utcnow()],
            key=lambda x: x.deadline
        )[:5]

        return render_template('main/dashboard.html',
                               total_projects=total_projects,
                               total_tasks=total_tasks,
                               pending_tasks=pending_tasks,
                               completed_tasks=completed_tasks,
                               recent_tasks=recent_tasks,
                               upcoming_tasks=upcoming_tasks,
                               team_members=team_members,
                               metrics=metrics,
                               now=datetime.utcnow(),
                               title='Dashboard')

    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('auth_bp.login'))
