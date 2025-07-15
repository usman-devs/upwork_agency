from app import create_app
from app.models import db, User, SkillsDirectory, UserSkills, Jobs, Project, Proposal
from faker import Faker
from datetime import date, timedelta
import random
from sqlalchemy import text
from werkzeug.security import generate_password_hash

app = create_app()
fake = Faker()

# JOBS SEEDING
with app.app_context():
    engine = db.engine
    # Disable foreign key checks
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
    db.drop_all()
    # Re-enable foreign key checks
    with engine.connect() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    db.session.commit()
    db.create_all()

    categories = ["Web Development", "Design", "Data Analysis", "Marketing"]
    skills = {
        "Web Development": "Flask, SQLAlchemy, HTML, CSS",
        "Design": "Photoshop, Illustrator, Figma",
        "Data Analysis": "Python, Pandas, Excel",
        "Marketing": "SEO, Google Ads, Content Writing"
    }

    # Generate random jobs
    jobs = []
    for i in range(10):
        job_id = f"JOB{100 + i}"
        cat = random.choice(categories)
        job = Jobs(
            job_id=job_id,
            title=fake.sentence(nb_words=6),
            description=fake.paragraph(nb_sentences=4),
            connects_required=random.randint(2, 6),
            category=cat,
            skills_requested=skills[cat],
            date_posted=date.today() - timedelta(days=random.randint(1, 10)),
            deadline=date.today() + timedelta(days=random.randint(10, 30)),
            stage="Open",
            expected_cost=round(random.uniform(200, 500), 2),
            expected_earning=round(random.uniform(300, 800), 2),
            client_rating=round(random.uniform(4.0, 5.0), 2),
            feasibility_score=round(random.uniform(75.0, 99.9), 2),
            link=fake.url()
        )
        jobs.append(job)
    db.session.add_all(jobs)


    # USERS SEEDING
    users = []
    for _ in range(5):
        email = fake.unique.email()
        user = User(
            email=email,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            password=generate_password_hash("Default1"),
            contact=fake.phone_number(),
            upwork_profile=fake.url(),
            connects_balance=random.randint(10, 60),
            title=fake.job(),
            hourly_rate=round(random.uniform(15, 50), 2),
            milestone_rate=round(random.uniform(100, 500), 2)
        )
        users.append(user)
    db.session.add_all(users)


    # SKILLS SEEDING
    skills = [
        SkillsDirectory(skill_version="Flask_v1", category="Backend", sub_category="Python"),
        SkillsDirectory(skill_version="Vue_v3", category="Frontend", sub_category="JavaScript"),
        SkillsDirectory(skill_version="SQLA_v1", category="Database", sub_category="ORM")
    ]
    db.session.add_all(skills)


    # USER SKILLS SEEDING
    user_skills = []
    for user in users:
        skill = random.choice(skills)
        entry = UserSkills(
            email=user.email,
            skill_version=skill.skill_version,
            proficiency_level=random.choice(["Beginner", "Intermediate", "Expert"])
        )
        user_skills.append(entry)
    db.session.add_all(user_skills)


    # PROPOSALS AND PROJECTS SEEDING
    proposals = []
    projects = []

    for job in Jobs.query.limit(3).all():
        owner = random.choice(users)
        proposal = Proposal(
            owner_email=owner.email,
            job_id=job.job_id,
            date=job.date_posted
        )
        project = Project(
            owner_email=owner.email,
            job_id=job.job_id,
            title=job.title,
            description=job.description,
            created_at=job.date_posted
        )
        projects.append(project)
        proposals.append(proposal)

    db.session.add_all(proposals + projects)
    db.session.commit()