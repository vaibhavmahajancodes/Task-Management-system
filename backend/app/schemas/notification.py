from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str = Field(min_length=1, max_length=500,)
    notif_type: NotificationType
    link: str = None = None
    is_read: bool
    created_at: datetime


class UnreadCount(BaseModel):
    unread_count: int = Field(ge=0)
