from datetime import datetime
from flask import render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from flask_caching import Cache
from app.models import Task, Project, Notification, User, Bid
from app.main import bp
from app.upwork.job_scraper import scrape_upwork_jobs
from app import cache, current_app, db
from app.utils.gemini import generate_proposal
from app.utils.email import send_opportunity_email

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    """Enhanced dashboard with role-specific views and metrics"""
    try:
        # Role-based data filtering
        if current_user.role == 'admin':
            projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
            tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
            team_members = User.query.filter(User.role != 'admin').limit(5).all()
            
            # Admin-specific metrics
            active_projects = Project.query.filter_by(status='active').count()
            pending_bids = Bid.query.filter_by(status='draft').count()
            won_bids = Bid.query.filter_by(status='won').count()
            
        elif current_user.role == 'manager':
            projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
            tasks = Task.query.filter(
                (Task.project.has(Project.id.in_([p.id for p in projects])) |
                (Task.assignee_id == current_user.id)
            ).order_by(Task.created_at.desc()).limit(5).all()
            team_members = User.query.filter_by(availability=True).limit(5).all()
            
        else:  # member/freelancer
            projects = Project.query.join(Task).filter(
                Task.assignee_id == current_user.id
            ).order_by(Project.created_at.desc()).limit(5).all()
            tasks = Task.query.filter_by(assignee_id=current_user.id).order_by(
                Task.created_at.desc()).limit(5).all()
            team_members = []
        
        # Common metrics
        total_projects = len(projects)
        total_tasks = len(tasks)
        pending_tasks = sum(1 for t in tasks if t.status == 'todo')
        completed_tasks = sum(1 for t in tasks if t.status == 'completed')
        
        # Upcoming deadlines (role-specific)
        if current_user.role in ['admin', 'manager']:
            upcoming_tasks = Task.query.filter(
                Task.deadline > datetime.utcnow()
            ).order_by(Task.deadline.asc()).limit(5).all()
        else:
            upcoming_tasks = Task.query.filter(
                Task.assignee_id == current_user.id,
                Task.deadline > datetime.utcnow()
            ).order_by(Task.deadline.asc()).limit(5).all()
        
        return render_template('main/dashboard.html',
                            total_projects=total_projects,
                            total_tasks=total_tasks,
                            pending_tasks=pending_tasks,
                            completed_tasks=completed_tasks,
                            projects=projects,
                            tasks=tasks,
                            team_members=team_members,
                            upcoming_tasks=upcoming_tasks,
                            now=datetime.utcnow(),
                            active_projects=active_projects if current_user.role == 'admin' else None,
                            pending_bids=pending_bids if current_user.role == 'admin' else None,
                            won_bids=won_bids if current_user.role == 'admin' else None)
    
    except Exception as e:
        flash('Error loading dashboard data. Please try again.', 'danger')
        current_app.logger.error(f"Dashboard error: {str(e)}")
        return redirect(url_for('main.home'))

@bp.route('/jobs')
@login_required
@cache.cached(timeout=300, key_prefix='job_listings')
def job_list():
    """Job listings with feasibility analysis and HTMX support"""
    try:
        if request.headers.get('HX-Request'):  # HTMX request
            jobs = scrape_upwork_jobs() or []
            return render_template('main/_jobs_list.html', jobs=jobs)
        
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        jobs = scrape_upwork_jobs() or []
        
        if not jobs:
            flash('No active job listings found.', 'info')
        
        # Apply admin-defined smart bidding rules
        if current_user.role == 'admin':
            min_budget = float(request.args.get('min_budget', 0))
            jobs = [job for job in jobs if job.get('budget', 0) >= min_budget]
        
        # Pagination
        total_jobs = len(jobs)
        paginated_jobs = jobs[(page-1)*per_page : page*per_page]
        total_pages = (total_jobs + per_page - 1) // per_page
        
        return render_template('main/jobs.html',
                            jobs=paginated_jobs,
                            page=page,
                            total_pages=total_pages,
                            total_jobs=total_jobs)
    
    except Exception as e:
        flash('Failed to retrieve job listings. Please try again later.', 'danger')
        current_app.logger.error(f"Job listings error: {str(e)}")
        return render_template('main/jobs.html', jobs=[])

@bp.route('/jobs/analyze/<job_id>')
@login_required
def analyze_job(job_id):
    """Analyze job feasibility and generate proposal"""
    if current_user.role not in ['admin', 'manager']:
        flash('You do not have permission to analyze jobs.', 'danger')
        return redirect(url_for('main.job_list'))
    
    try:
        jobs = scrape_upwork_jobs() or []
        job = next((j for j in jobs if j.get('id') == job_id), None)
        
        if not job:
            flash('Job not found.', 'danger')
            return redirect(url_for('main.job_list'))
        
        # Generate proposal using Gemini
        proposal = generate_proposal(job)
        
        # Calculate feasibility
        budget = job.get('budget', 0)
        expected_hours = job.get('expected_hours', 1)
        hourly_rate = current_app.config.get('DEFAULT_HOURLY_RATE', 25)
        feasibility_score = (budget / (expected_hours * hourly_rate)) * 100
        
        return render_template('main/job_analysis.html',
                            job=job,
                            proposal=proposal,
                            feasibility_score=feasibility_score)
    
    except Exception as e:
        flash('Failed to analyze job. Please try again later.', 'danger')
        current_app.logger.error(f"Job analysis error: {str(e)}")
        return redirect(url_for('main.job_list'))

@bp.route('/jobs/submit_bid', methods=['POST'])
@login_required
def submit_bid():
    """Submit a bid for a job"""
    if current_user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        job_id = request.form.get('job_id')
        proposal_text = request.form.get('proposal_text')
        connects_used = int(request.form.get('connects_used', 2))
        feasibility_score = float(request.form.get('feasibility_score', 80))
        
        # Create a new project (placeholder until won)
        project = Project(
            title=f"Potential Project - {job_id}",
            description="Project created from bid submission",
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # Create the bid
        bid = Bid(
            upwork_job_id=job_id,
            proposal_text=proposal_text,
            connects_used=connects_used,
            feasibility_score=feasibility_score,
            status='submitted',
            project_id=project.id,
            created_at=datetime.utcnow()
        )
        db.session.add(bid)
        db.session.commit()
        
        # Send email notification to admins
        send_opportunity_email(
            job_id=job_id,
            proposal=proposal_text,
            feasibility_score=feasibility_score,
            project_id=project.id
        )
        
        flash('Bid submitted successfully!', 'success')
        return jsonify({'success': True, 'redirect': url_for('main.dashboard')})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Bid submission error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/jobs/refresh')
@login_required
def refresh_jobs():
    """Manual cache refresh endpoint with HTMX support"""
    try:
        cache.delete('job_listings')
        
        if request.headers.get('HX-Request'):
            jobs = scrape_upwork_jobs() or []
            return render_template('main/_jobs_list.html', jobs=jobs)
        
        flash('Job listings refreshed successfully', 'success')
    except Exception as e:
        flash('Refresh failed', 'danger')
        current_app.logger.error(f"Refresh error: {str(e)}")
    return redirect(url_for('main.job_list'))

@bp.route('/notifications')
@login_required
def notifications():
    """Display user notifications with HTMX support"""
    try:
        user_notifications = Notification.query.filter_by(
            user_id=current_user.id
        ).order_by(Notification.created_at.desc()).limit(10).all()
        
        if request.headers.get('HX-Request'):
            return render_template('main/_notifications_list.html', 
                               notifications=user_notifications)
        
        return render_template('main/notifications.html', 
                            notifications=user_notifications)
    except Exception as e:
        flash('Error loading notifications', 'danger')
        current_app.logger.error(f"Notifications error: {str(e)}")
        return redirect(url_for('main.dashboard'))

@bp.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read (HTMX)"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        if notification.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.read = True
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Notification mark read error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/workload')
@login_required
def workload():
    """Team workload overview (for managers/admins)"""
    if current_user.role not in ['admin', 'manager']:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        team_members = User.query.filter(User.role != 'admin').all()
        workload_data = []
        
        for member in team_members:
            total_tasks = Task.query.filter_by(assignee_id=member.id).count()
            pending_tasks = Task.query.filter_by(
                assignee_id=member.id,
                status='todo'
            ).count()
            in_progress_tasks = Task.query.filter_by(
                assignee_id=member.id,
                status='in_progress'
            ).count()
            
            workload_data.append({
                'member': member,
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'availability': member.availability
            })
        
        return render_template('main/workload.html',
                            workload_data=workload_data)
    
    except Exception as e:
        flash('Error loading workload data', 'danger')
        current_app.logger.error(f"Workload error: {str(e)}")
        return redirect(url_for('main.dashboard'))