from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.db import Base


class AuditLog(Base):
    """
    Generic audit trail row. `action` uses a dotted convention such as
    'task.created', 'task.deleted', 'project.updated', 'auth.login'.
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True)  # "task" | "project" | "user" | ...
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # human readable description / JSON string
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action!r}>"
