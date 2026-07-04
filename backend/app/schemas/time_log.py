from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserSummary


class TimeLogStart(BaseModel):
    task_id: int = Field(gt=0)


class TimeLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    user: Optional[UserSummary] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: int= Field (ge=0)
    is_running: bool = False


class TimesheetEntry(BaseModel):
    user: Optional [UserSummary] = None
    total_seconds: int = Field(ge=0)
    entry_count: int = Field(ge=0)
