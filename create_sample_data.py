from app import create_app, db
from app.models import User, Project, Task
from flask_bcrypt import generate_password_hash

def create_sample_data():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create users with hashed passwords
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123').decode('utf-8'),
            role='admin'
        )
        manager = User(
            username='manager',
            email='manager@example.com',
            password=generate_password_hash('manager123').decode('utf-8'),
            role='manager'
        )
        member = User(
            username='member',
            email='member@example.com',
            password=generate_password_hash('member123').decode('utf-8'),
            role='member'
        )

        db.session.add_all([admin, manager, member])
        db.session.commit()

        # Create project
        project = Project(
            title='Website Redesign',
            description='Client website redesign project',
            creator=manager
        )
        db.session.add(project)
        db.session.commit()

        # Create tasks
        task1 = Task(
            title='Design homepage',
            description='Create new homepage design',
            status='todo',
            priority='high',
            project=project,
            assignee=member
        )
        task2 = Task(
            title='Develop API',
            description='Build REST API endpoints',
            status='in_progress',
            priority='medium',
            project=project,
            assignee=member
        )
        db.session.add_all([task1, task2])
        db.session.commit()

        print("Sample data created successfully!")

if __name__ == '__main__':
    create_sample_data()