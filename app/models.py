from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_projects = db.relationship('Project', backref='creator', lazy=True)
    assigned_tasks = db.relationship('Task', backref='assignee', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    bids = db.relationship('Bid', backref='bidder', lazy=True)  # Added relationship to Bid

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    
    # Foreign Keys
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    bids = db.relationship('Bid', backref='project', lazy=True)  # Added relationship to Bid

    def __repr__(self):
        return f"Project('{self.title}')"

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='todo')
    priority = db.Column(db.String(10), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deadline = db.Column(db.DateTime)
    
    # Foreign Keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"Task('{self.title}', '{self.status}')"

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class Bid(db.Model):
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    upwork_job_id = db.Column(db.String(100), nullable=False)
    proposal_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, submitted, won, lost
    connects_used = db.Column(db.Integer, default=2)
    feasibility_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"Bid('{self.upwork_job_id}', '{self.status}')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))