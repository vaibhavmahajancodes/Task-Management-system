"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

user_role_enum = sa.Enum("admin", "project_manager", "team_member", name="userrole")
project_status_enum = sa.Enum("planning", "active", "on_hold", "completed", "archived", name="projectstatus")
project_priority_enum = sa.Enum("low", "medium", "high", "critical", name="projectpriority")
task_status_enum = sa.Enum("todo", "in_progress", "review", "completed", name="taskstatus")
task_priority_enum = sa.Enum("low", "medium", "high", "critical", name="taskpriority")
notification_type_enum = sa.Enum(
    "task_assigned",
    "task_updated",
    "mention",
    "comment",
    "deadline_reminder",
    "project_update",
    "project_invite",
    name="notificationtype",
)


def upgrade() -> None:
    bind = op.get_bind()

    user_role_enum.create(bind, checkfirst=True)
    project_status_enum.create(bind, checkfirst=True)
    project_priority_enum.create(bind, checkfirst=True)
    task_status_enum.create(bind, checkfirst=True)
    task_priority_enum.create(bind, checkfirst=True)
    notification_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("full_name", sa.String(150), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role_enum, nullable=False, server_default="team_member"),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("job_title", sa.String(150), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("theme_preference", sa.String(10), nullable=False, server_default="light"),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
        sa.Column("last_login_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(200), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", project_status_enum, nullable=False, server_default="planning"),
        sa.Column("priority", project_priority_enum, nullable=False, server_default="medium"),
        sa.Column("deadline", sa.Date, nullable=True),
        sa.Column("owner_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("is_archived", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("color", sa.String(7), nullable=False, server_default="#2F6F5E"),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "project_members",
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False, index=True),
        sa.Column("color", sa.String(7), nullable=False, server_default="#64748B"),
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("title", sa.String(250), nullable=False, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("status", task_status_enum, nullable=False, server_default="todo"),
        sa.Column("priority", task_priority_enum, nullable=False, server_default="medium"),
        sa.Column("due_date", sa.DateTime, nullable=True, index=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("assigned_to", sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("parent_task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("position", sa.Integer, nullable=False, server_default="0"),
        sa.Column("estimated_hours", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "task_tags",
        sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("notif_type", notification_type_enum, nullable=False),
        sa.Column("link", sa.String(300), nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=False, server_default=sa.false(), index=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
    )

    op.create_table(
        "attachments",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("file_size", sa.Integer, nullable=False),
        sa.Column("content_type", sa.String(150), nullable=True),
        sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("uploaded_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True, index=True),
        sa.Column("action", sa.String(100), nullable=False, index=True),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.Integer, nullable=True),
        sa.Column("details", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True, index=True),
    )

    op.create_table(
        "time_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("task_id", sa.Integer, sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("start_time", sa.DateTime, nullable=False),
        sa.Column("end_time", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("revoked", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("token", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("used", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("password_reset_tokens")
    op.drop_table("refresh_tokens")
    op.drop_table("time_logs")
    op.drop_table("audit_logs")
    op.drop_table("attachments")
    op.drop_table("notifications")
    op.drop_table("comments")
    op.drop_table("task_tags")
    op.drop_table("tasks")
    op.drop_table("tags")
    op.drop_table("project_members")
    op.drop_table("projects")
    op.drop_table("users")

    bind = op.get_bind()
    notification_type_enum.drop(bind, checkfirst=True)
    task_priority_enum.drop(bind, checkfirst=True)
    task_status_enum.drop(bind, checkfirst=True)
    project_priority_enum.drop(bind, checkfirst=True)
    project_status_enum.drop(bind, checkfirst=True)
    user_role_enum.drop(bind, checkfirst=True)
