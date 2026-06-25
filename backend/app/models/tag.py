from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base
from app.models.associations import task_tags


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = {"extend_existing": True} 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    color = Column(String(7), default="#64748B", nullable=False)  # hex colour

    tasks = relationship("Task", secondary=task_tags, back_populates="tags")

    def __repr__(self) -> str:
        return f"<Tag id={self.id} name={self.name!r}>"
