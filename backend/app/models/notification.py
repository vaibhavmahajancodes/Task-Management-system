import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


class NotificationType(str, enum.Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_UPDATED = "task_updated"
    MENTION = "mention"
    COMMENT = "comment"
    DEADLINE_REMINDER = "deadline_reminder"
    PROJECT_UPDATE = "project_update"
    PROJECT_INVITE = "project_invite"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String(500), nullable=False)
    notif_type = Column(String(50), nullable=False)
    link = Column(String(300), nullable=True)  # e.g. /projects/3/tasks/12
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="notifications", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user_id={self.user_id} type={self.notif_type}>"
