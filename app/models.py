from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


class User(db.Model):
    __tablename__ = 'user'
    
    email = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    contact  = db.Column(db.String(20))
    password  = db.Column(db.String(255))
    upwork_profile = db.Column(db.Text)
    connects_balance = db.Column(db.Integer)
    title = db.Column(db.String(255))
    hourly_rate = db.Column(db.Numeric(10, 2))
    milestone_rate = db.Column(db.Numeric(10, 2))

    # Relationships
    skills = db.relationship('UserSkills', back_populates='user', cascade="all, delete-orphan")
    proposals = db.relationship('Proposal', back_populates='owner', cascade="all, delete-orphan")
    # projects = db.relationship('Project', back_populates='owner', cascade="all, delete-orphan")
    assigned_tasks = db.relationship('Tasks', back_populates='assigned_to', foreign_keys='Tasks.assigned_to_email')
    managed_users = db.relationship('Relationships', foreign_keys='Relationships.manager_email', back_populates='manager')
    managers = db.relationship('Relationships', foreign_keys='Relationships.user_email', back_populates='user')


class SkillsDirectory(db.Model):
    __tablename__ = 'skills_directory'
    
    skill_version = db.Column(db.String(100), primary_key=True)
    category = db.Column(db.String(100))
    sub_category = db.Column(db.String(100))

    users = db.relationship('UserSkills', back_populates='skill', cascade="all, delete-orphan")


class UserSkills(db.Model):
    __tablename__ = 'user_skills'
    
    email = db.Column(db.String(255), db.ForeignKey('user.email'), primary_key=True)
    skill_version = db.Column(db.String(100), db.ForeignKey('skills_directory.skill_version'), primary_key=True)
    proficiency_level = db.Column(db.String(50))

    # Relationships
    user = db.relationship('User', back_populates='skills')
    skill = db.relationship('SkillsDirectory', back_populates='users')


class Relationships(db.Model):
    __tablename__ = 'relationships'
    
    user_email = db.Column(db.String(255), db.ForeignKey('user.email'), primary_key=True)
    manager_email = db.Column(db.String(255), db.ForeignKey('user.email'), primary_key=True)
    role = db.Column(db.String(50))
    status = db.Column(db.String(50))

    # Relationships
    user = db.relationship('User', foreign_keys=[user_email], back_populates='managers')
    manager = db.relationship('User', foreign_keys=[manager_email], back_populates='managed_users')


class Jobs(db.Model):
    __tablename__ = 'jobs'
    
    job_id = db.Column(db.String(100), primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    connects_required = db.Column(db.Integer)
    category = db.Column(db.String(100))
    skills_requested = db.Column(db.Text)
    date_posted = db.Column(db.Date)
    deadline = db.Column(db.Date)
    stage = db.Column(db.String(100))
    expected_cost = db.Column(db.Numeric(10, 2))
    expected_earning = db.Column(db.Numeric(10, 2))
    client_rating = db.Column(db.Numeric(3, 2))
    feasibility_score = db.Column(db.Numeric(4, 2))
    link = db.Column(db.String(255))

    proposals = db.relationship('Proposal', back_populates='job', cascade="all, delete-orphan")
    # projects = db.relationship('Project', back_populates='job', cascade="all, delete-orphan")


class Proposal(db.Model):
    __tablename__ = 'proposal'
    
    owner_email = db.Column(db.String(255), db.ForeignKey('user.email'), primary_key=True)
    job_id = db.Column(db.String(100), db.ForeignKey('jobs.job_id'), primary_key=True)
    date = db.Column(db.Date)

    # Relationships
    owner = db.relationship('User', back_populates='proposals')
    job = db.relationship('Jobs', back_populates='proposals')
    # project = db.relationship('Project', back_populates='proposal', uselist=False, cascade="all, delete-orphan")


class Project(db.Model):
    __tablename__ = 'project'
    
    owner_email = db.Column(db.String(255), db.ForeignKey('proposal.owner_email'), primary_key=True)
    job_id = db.Column(db.String(100), db.ForeignKey('proposal.job_id'), primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    created_at = db.Column(db.Date)

    # Relationships
    # proposal = db.relationship('Proposal', back_populates='project')
    tasks = db.relationship('Tasks', back_populates='project', cascade="all, delete-orphan")
    # owner = db.relationship('User', back_populates='projects')
    # job = db.relationship('Jobs', back_populates='projects')


class Tasks(db.Model):
    __tablename__ = 'tasks'
    
    owner_email = db.Column(db.String(255), primary_key=True)
    job_id = db.Column(db.String(100), primary_key=True)
    created_datetime = db.Column(db.DateTime, primary_key=True)
    assigned_to_email = db.Column(db.String(255), db.ForeignKey('user.email'))
    deadline_datetime = db.Column(db.DateTime)
    completed_datetime = db.Column(db.DateTime)
    priority = db.Column(db.String(50))
    description = db.Column(db.Text)

    # Foreign keys to Project composite key
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['owner_email', 'job_id'],
            ['project.owner_email', 'project.job_id']
        ),
    )

    # Relationships
    project = db.relationship('Project', back_populates='tasks')
    assigned_to = db.relationship('User', back_populates='assigned_tasks')