from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Task, User, Project
from app.tasks import bp
from app.tasks.forms import CreateTaskForm, UpdateTaskForm, AssignTaskForm
from datetime import datetime

@bp.route('/')
@login_required
def list_tasks():
    """List all tasks based on user role"""
    if current_user.role == 'admin':
        tasks = Task.query.all()
    elif current_user.role == 'manager':
        # Managers see tasks from projects they manage
        tasks = Task.query.join(Project).filter(Project.manager_id == current_user.id).all()
    else:
        # Regular members see only their assigned tasks
        tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    
    return render_template('tasks/list.html', tasks=tasks)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Create a new task"""
    form = CreateTaskForm()
    
    # Populate project dropdown for admins/managers
    if current_user.role in ['admin', 'manager']:
        form.project_id.choices = [(p.id, p.title) for p in Project.query.all()]
    else:
        form.project_id.choices = []
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status='todo',  # Default status
            priority=form.priority.data,
            deadline=form.deadline.data,
            project_id=form.project_id.data,
            created_by=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/create.html', form=form)

@bp.route('/<int:task_id>')
@login_required
def view_task(task_id):
    """View task details"""
    task = Task.query.get_or_404(task_id)
    # Authorization check
    if not (current_user.role == 'admin' or 
            (current_user.role == 'manager' and task.project.manager_id == current_user.id) or
            task.assignee_id == current_user.id):
        flash('You are not authorized to view this task', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/view.html', task=task)

@bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task"""
    task = Task.query.get_or_404(task_id)
    
    # Authorization check
    if not (current_user.role == 'admin' or 
            (current_user.role == 'manager' and task.project.manager_id == current_user.id)):
        flash('You are not authorized to edit this task', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    form = UpdateTaskForm(obj=task)
    
    if form.validate_on_submit():
        form.populate_obj(task)
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/edit.html', form=form, task=task)

@bp.route('/<int:task_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_task(task_id):
    """Assign task to a team member"""
    task = Task.query.get_or_404(task_id)
    
    # Authorization check
    if not (current_user.role == 'admin' or 
            (current_user.role == 'manager' and task.project.manager_id == current_user.id)):
        flash('You are not authorized to assign this task', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    form = AssignTaskForm()
    
    # Populate assignee dropdown with team members
    form.assignee_id.choices = [(user.id, user.username) 
                               for user in User.query.filter(User.role.in_(['member', 'manager'])).all()]
    
    if form.validate_on_submit():
        task.assignee_id = form.assignee_id.data
        task.status = 'in_progress'  # Automatically change status when assigned
        db.session.commit()
        flash('Task assigned successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/assign.html', form=form, task=task)

@bp.route('/<int:task_id>/status', methods=['POST'])
@login_required
def update_status(task_id):
    """Update task status (HTMX compatible)"""
    task = Task.query.get_or_404(task_id)
    
    # Authorization check
    if not (current_user.role == 'admin' or 
            task.assignee_id == current_user.id or
            (current_user.role == 'manager' and task.project.manager_id == current_user.id)):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    new_status = request.form.get('status')
    if new_status in ['todo', 'in_progress', 'review', 'completed']:
        task.status = new_status
        db.session.commit()
        
        if request.headers.get('HX-Request'):
            # HTMX request - return partial content
            return render_template('tasks/_status_badge.html', task=task)
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Invalid status'}), 400

@bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    
    # Authorization check
    if not (current_user.role == 'admin' or 
            (current_user.role == 'manager' and task.project.manager_id == current_user.id)):
        flash('You are not authorized to delete this task', 'danger')
        return redirect(url_for('tasks.list_tasks'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.list_tasks'))