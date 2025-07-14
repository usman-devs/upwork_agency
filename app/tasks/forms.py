from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional
from datetime import datetime

class CreateTaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField('Status', 
                       choices=[
                           ('todo', 'To Do'),
                           ('in_progress', 'In Progress'),
                           ('review', 'In Review'),
                           ('completed', 'Completed')
                       ],
                       default='todo')
    priority = SelectField('Priority',
                         choices=[
                             ('low', 'Low'),
                             ('medium', 'Medium'),
                             ('high', 'High')
                         ],
                         default='medium')
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Create Task')

class UpdateTaskForm(FlaskForm):
    title = StringField('Task Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    status = SelectField('Status', 
                       choices=[
                           ('todo', 'To Do'),
                           ('in_progress', 'In Progress'),
                           ('review', 'In Review'),
                           ('completed', 'Completed')
                       ])
    priority = SelectField('Priority',
                         choices=[
                             ('low', 'Low'),
                             ('medium', 'Medium'),
                             ('high', 'High')
                         ])
    deadline = DateField('Deadline', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Update Task')

class AssignTaskForm(FlaskForm):
    assignee = SelectField('Assign To', coerce=int)
    submit = SubmitField('Assign Task')
