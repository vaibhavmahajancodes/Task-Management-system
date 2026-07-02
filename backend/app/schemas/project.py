from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectPriority, ProjectStatus
from app.schemas.user import UserSummary


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    priority: ProjectPriority = ProjectPriority.MEDIUM
    deadline: Optional[date] = None
    color: str = Field(default="#2F6F5E", pattern="^#[0-9A-Fa-f]{6}$")


class ProjectCreate(ProjectBase):
    member_ids: List[int] = Field(default_factory=list)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    deadline: Optional[date] = None
    color: Optional[str] = Field(default=None, pattern="^#[0-9A-Fa-f]{6}$")


class ProjectMemberUpdate(BaseModel):
    user_id: int


class ProjectOut(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    owner: UserSummary
    members: List[UserSummary] = Field(default_factory=list)
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    task_count: int 
    completed_task_count: int
    progress_percent: float = 0.0


class ProjectListItem(BaseModel):
    """Slimmer shape for list views / dropdowns."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: ProjectStatus
    priority: ProjectPriority
    deadline: Optional[date] = None
    color: str
    is_archived: bool
    progress_percent: float = 0.0
    task_count: int = 0
