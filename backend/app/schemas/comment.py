from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserSummary


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    task_id: int
    user: UserSummary
    created_at: datetime
    updated_at: datetime
    mentioned_usernames: List[str] = Field(default_factory=list)
