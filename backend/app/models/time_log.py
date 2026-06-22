from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database.db import Base


class TimeLog(Base):
    """A single start/stop timer entry logged against a task by a user."""

    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task = relationship("Task", back_populates="time_logs")
    user = relationship("User", back_populates="time_logs")

    @property
    def duration_seconds(self) -> int:
        if self.end_time is None:
            return 0
        return int((self.end_time - self.start_time).total_seconds())

    @property
    def is_running(self) -> bool:
        return self.end_time is None

    def __repr__(self) -> str:
        return f"<TimeLog id={self.id} task_id={self.task_id} running={self.is_running}>"
