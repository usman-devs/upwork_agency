from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from flask_caching import Cache
from sqlalchemy import func, or_
from app.models import Task, Project, Notification, User, Bid
from app import db
from app.utils.helpers import calculate_feasibility

# Initialize Blueprint
bp = Blueprint('main', __name__)

# Initialize cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

@bp.route('/')
def index():
    return render_template('main/index.html')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with role-specific views"""
    try:
        # Base queries
        projects_query = Project.query
        tasks_query = Task.query
        
        # Role-based filtering
        if current_user.role == 'admin':
            projects = projects_query.order_by(Project.created_at.desc()).limit(5).all()
            tasks = tasks_query.order_by(Task.created_at.desc()).limit(5).all()
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
            ).order_by(Task.created_at.desc()).limit(5).all()
            team_members = User.query.filter_by(availability=True).limit(5).all()
            metrics = {}
            
        else:  # member
            projects = projects_query.join(Task).filter(
                Task.assignee_id == current_user.id
            ).order_by(Project.created_at.desc()).limit(5).all()
            tasks = tasks_query.filter_by(assignee_id=current_user.id).order_by(
                Task.created_at.desc()).limit(5).all()
            team_members = []
            metrics = {}

        # Common metrics
        common_metrics = {
            'total_tasks': len(tasks),
            'pending_tasks': sum(1 for t in tasks if t.status == 'todo'),
            'overdue_tasks': sum(1 for t in tasks if t.deadline and t.deadline < datetime.utcnow()),
        }

        return render_template('main/dashboard.html',
                           projects=projects,
                           tasks=tasks,
                           team_members=team_members,
                           metrics={**common_metrics, **metrics},
                           now=datetime.utcnow(),
                           title='Dashboard')

    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        flash('Error loading dashboard', 'danger')
        return redirect(url_for('auth.login'))

@bp.route('/jobs')
@login_required
def job_list():
    """Job listings page"""
    try:
        # Mock job data - replace with actual Upwork API or scraping
        jobs = [
            {
                'id': '1',
                'title': 'Website Development',
                'description': 'Need a WordPress website',
                'budget': 500,
                'skills': ['WordPress', 'PHP'],
                'posted': '2 days ago'
            },
            {
                'id': '2', 
                'title': 'Data Analysis',
                'description': 'Python data analysis project',
                'budget': 800,
                'skills': ['Python', 'Pandas'],
                'posted': '1 day ago'
            }
        ]
        
        return render_template('main/jobs.html', jobs=jobs, title='Job Listings')

    except Exception as e:
        current_app.logger.error(f"Jobs error: {str(e)}", exc_info=True)
        flash('Error loading jobs', 'danger')
        return redirect(url_for('main.dashboard'))

@bp.route('/workload')
@login_required
def workload():
    """Team workload overview"""
    try:
        if current_user.role not in ['admin', 'manager']:
            flash('Access denied', 'danger')
            return redirect(url_for('main.dashboard'))
            
        team_members = User.query.filter(User.role != 'admin').all()
        workload_data = []
        
        for member in team_members:
            tasks = Task.query.filter_by(assignee_id=member.id).all()
            workload_data.append({
                'member': member,
                'total_tasks': len(tasks),
                'pending_tasks': sum(1 for t in tasks if t.status == 'todo'),
                'completed_tasks': sum(1 for t in tasks if t.status == 'completed'),
            })
            
        return render_template('main/workload.html', 
                            workload_data=workload_data,
                            title='Team Workload')

    except Exception as e:
        current_app.logger.error(f"Workload error: {str(e)}", exc_info=True)
        flash('Error loading workload data', 'danger')
        return redirect(url_for('main.dashboard'))

def generate_proposal(job, user):
    """Generate proposal text"""
    try:
        # Replace with actual Gemini API integration
        return f"""Dear Client,

I'm {user.username} from our agency and we'd love to help with your {job['title']} project. 
Based on the requirements, we estimate we can deliver this within your budget of ${job['budget']}.

Our team has extensive experience with {', '.join(job['skills'])} and we're confident we can deliver excellent results.

Looking forward to your response!

Best regards,
{user.username}"""
    except Exception as e:
        current_app.logger.error(f"Proposal generation error: {str(e)}")
        return "Unable to generate proposal at this time."