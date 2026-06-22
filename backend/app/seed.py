"""
Populates the database with a ready-to-explore demo dataset.

Usage:
    python -m app.seed

Safe to re-run: it checks for existing records before inserting and will
not duplicate the admin account or sample project on a second run.
"""
from datetime import datetime, timedelta, timezone

from app.auth.security import hash_password
from app.database.db import Base, SessionLocal, engine
from app.models.project import Project, ProjectPriority, ProjectStatus
from app.models.tag import Tag
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User, UserRole

DEMO_USERS = [
    {"username": "admin", "email": "admin@taskmanager.local", "full_name": "Ava Administrator", "role": UserRole.ADMIN, "password": "Admin@12345"},
    {"username": "pmorgan", "email": "pm@taskmanager.local", "full_name": "Priya Morgan", "role": UserRole.PROJECT_MANAGER, "password": "Manager@12345"},
    {"username": "jchen", "email": "jchen@taskmanager.local", "full_name": "Jordan Chen", "role": UserRole.TEAM_MEMBER, "password": "Member@12345"},
    {"username": "rkapoor", "email": "rkapoor@taskmanager.local", "full_name": "Riya Kapoor", "role": UserRole.TEAM_MEMBER, "password": "Member@12345"},
]


def run():
    import app.models  # noqa: F401 ensure all models are registered

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        users_by_username = {}
        for spec in DEMO_USERS:
            existing = db.query(User).filter(User.username == spec["username"]).first()
            if existing:
                users_by_username[spec["username"]] = existing
                continue
            user = User(
                username=spec["username"],
                email=spec["email"],
                full_name=spec["full_name"],
                role=spec["role"],
                password_hash=hash_password(spec["password"]),
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            users_by_username[spec["username"]] = user
            print(f"Created user '{user.username}' ({spec['role'].value}) - password: {spec['password']}")

        tag_names = [("Backend", "#2F6F5E"), ("Frontend", "#E8A33D"), ("Bug", "#DC2626"), ("Design", "#7C3AED")]
        tags = {}
        for name, color in tag_names:
            tag = db.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name, color=color)
                db.add(tag)
                db.commit()
                db.refresh(tag)
            tags[name] = tag

        project = db.query(Project).filter(Project.name == "Website Relaunch").first()
        if not project:
            project = Project(
                name="Website Relaunch",
                description="Redesign and rebuild the marketing site with the new brand system.",
                status=ProjectStatus.ACTIVE,
                priority=ProjectPriority.HIGH,
                deadline=(datetime.now(timezone.utc) + timedelta(days=30)).date(),
                owner_id=users_by_username["pmorgan"].id,
                color="#2F6F5E",
            )
            project.members = [users_by_username["pmorgan"], users_by_username["jchen"], users_by_username["rkapoor"]]
            db.add(project)
            db.commit()
            db.refresh(project)
            print(f"Created project '{project.name}'")

            now = datetime.now(timezone.utc)
            demo_tasks = [
                {
                    "title": "Set up CI/CD pipeline",
                    "description": "Configure GitHub Actions to run tests and build Docker images on every push.",
                    "status": TaskStatus.COMPLETED,
                    "priority": TaskPriority.HIGH,
                    "assigned_to": users_by_username["jchen"].id,
                    "due_date": now - timedelta(days=2),
                    "completed_at": now - timedelta(days=3),
                    "tags": [tags["Backend"]],
                },
                {
                    "title": "Design new homepage hero section",
                    "description": "Explore 3 directions for the hero, present to stakeholders for sign-off.",
                    "status": TaskStatus.IN_PROGRESS,
                    "priority": TaskPriority.CRITICAL,
                    "assigned_to": users_by_username["rkapoor"].id,
                    "due_date": now + timedelta(days=2),
                    "tags": [tags["Design"]],
                },
                {
                    "title": "Fix mobile nav overlap bug",
                    "description": "The mobile menu overlaps the search bar on screens under 380px wide.",
                    "status": TaskStatus.REVIEW,
                    "priority": TaskPriority.MEDIUM,
                    "assigned_to": users_by_username["jchen"].id,
                    "due_date": now + timedelta(days=5),
                    "tags": [tags["Bug"], tags["Frontend"]],
                },
                {
                    "title": "Migrate blog content to new CMS",
                    "description": "Export all posts from the old CMS and import into the new headless CMS.",
                    "status": TaskStatus.TODO,
                    "priority": TaskPriority.LOW,
                    "assigned_to": None,
                    "due_date": now + timedelta(days=14),
                    "tags": [],
                },
                {
                    "title": "Write API documentation",
                    "description": "Document every public endpoint with example requests and responses.",
                    "status": TaskStatus.TODO,
                    "priority": TaskPriority.MEDIUM,
                    "assigned_to": users_by_username["jchen"].id,
                    "due_date": now + timedelta(days=10),
                    "tags": [tags["Backend"]],
                },
            ]
            for i, spec in enumerate(demo_tasks):
                task = Task(
                    title=spec["title"],
                    description=spec["description"],
                    status=spec["status"],
                    priority=spec["priority"],
                    assigned_to=spec["assigned_to"],
                    due_date=spec["due_date"],
                    completed_at=spec.get("completed_at"),
                    project_id=project.id,
                    created_by=users_by_username["pmorgan"].id,
                    position=i,
                )
                task.tags = spec["tags"]
                db.add(task)
            db.commit()
            print(f"Created {len(demo_tasks)} demo tasks.")

        print("\nSeed complete. Demo accounts:")
        for spec in DEMO_USERS:
            print(f"  {spec['username']:10s} / {spec['password']:18s} ({spec['role'].value})")
    finally:
        db.close()


if __name__ == "__main__":
    run()
