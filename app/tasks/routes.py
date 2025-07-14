from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Task, User
from app.tasks import bp
from app.tasks.forms import CreateTaskForm, UpdateTaskForm, AssignTaskForm
from datetime import datetime

@bp.route('/tasks')
@login_required
def list_tasks():
    # Get tasks based on user role
    if current_user.role == 'admin':
        tasks = Task.query.all()
    elif current_user.role == 'manager':
        tasks = Task.query.filter(Task.project.has(creator_id=current_user.id)).all()
    else:
        tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    
    return render_template('tasks/list.html', tasks=tasks)

@bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = CreateTaskForm()
    
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
            priority=form.priority.data,
            deadline=form.deadline.data,
            created_by=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/create.html', form=form)

@bp.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = UpdateTaskForm(obj=task)
    
    if form.validate_on_submit():
        form.populate_obj(task)
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/edit.html', form=form, task=task)

@bp.route('/tasks/<int:task_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = AssignTaskForm()
    
    # Populate assignee dropdown with team members
    form.assignee.choices = [(user.id, user.username) for user in User.query.filter(User.role.in_(['member', 'manager'])).all()]
    
    if form.validate_on_submit():
        task.assignee_id = form.assignee.data
        task.status = 'in_progress'  # Automatically change status when assigned
        db.session.commit()
        flash('Task assigned successfully!', 'success')
        return redirect(url_for('tasks.list_tasks'))
    
    return render_template('tasks/assign.html', form=form, task=task)

@bp.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('tasks.list_tasks'))