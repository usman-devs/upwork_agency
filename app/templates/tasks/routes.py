from flask import Blueprint, render_template
from models import Todo, Task  # Adjust path if needed

tasks_bp = Blueprint('tasks', __name__, template_folder='templates')

@tasks_bp.route('/todos')
def show_todos():
    todos = Todo.query.all()
    return render_template('tasks/todos.html', todos=todos)

@tasks_bp.route('/tasks')
def list_tasks():
    tasks = Task.query.all()
    return render_template('tasks/list.html', tasks=tasks)
