from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserSummary


class TimeLogStart(BaseModel):
    task_id: int


class TimeLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user: UserSummary
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: int
    is_running: bool


class TimesheetEntry(BaseModel):
    user: UserSummary
    total_seconds: int
    entry_count: int
