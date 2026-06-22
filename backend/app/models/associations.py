"""Many-to-many association tables (no model identity of their own)."""
from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database.db import Base

# A project has many members (team members assigned to it); a user can
# belong to many projects. The owner is tracked separately on Project.owner_id.
project_members = Table(
    "project_members",
    Base.metadata,
    Column("project_id", Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

# A task can have many labels/tags, and a tag can apply to many tasks.
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
