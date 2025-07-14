from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Explicit table name
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_projects = db.relationship('Project', backref='creator', lazy=True)
    assigned_tasks = db.relationship('Task', backref='assignee', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Project(db.Model):
    __tablename__ = 'projects'  # Explicit table name
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Project('{self.title}', '{self.description}')"

class Task(db.Model):
    __tablename__ = 'tasks'  # Explicit table name
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')
    priority = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"Task('{self.title}', '{self.status}')"

# User loader function should be after all models are defined
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }