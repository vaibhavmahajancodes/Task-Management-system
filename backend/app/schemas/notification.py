from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationType


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    notif_type: NotificationType
    link: Optional[str] = None
    is_read: bool
    created_at: datetime


class UnreadCount(BaseModel):
    unread_count: int
