"""
Importing every model here ensures `Base.metadata` is fully populated
in one place -- this is what Alembic's `env.py` imports for autogenerate,
and it's also what `Base.metadata.create_all()` uses in `seed.py` / tests.
"""
from app.models.associations import project_members, task_tags  # noqa: F401
from app.models.attachment import Attachment  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.comment import Comment  # noqa: F401
from app.models.notification import Notification, NotificationType  # noqa: F401
from app.models.project import Project, ProjectPriority, ProjectStatus  # noqa: F401
from app.models.refresh_token import PasswordResetToken, RefreshToken  # noqa: F401
from app.models.tag import Tag  # noqa: F401
from app.models.task import Task, TaskPriority, TaskStatus  # noqa: F401
from app.models.time_log import TimeLog  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401

__all__ = [
    "User",
    "UserRole",
    "Project",
    "ProjectStatus",
    "ProjectPriority",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "Comment",
    "Notification",
    "NotificationType",
    "Attachment",
    "AuditLog",
    "TimeLog",
    "RefreshToken",
    "PasswordResetToken",
    "Tag",
    "project_members",
    "task_tags",
]
