from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus
from app.schemas.user import UserSummary


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    color: str


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=250)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = Field(default=None, ge=0, le=2000)


class TaskCreate(TaskBase):
    project_id: int
    assigned_to: Optional[int] = None
    parent_task_id: Optional[int] = None
    tag_ids: List[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=250)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    estimated_hours: Optional[int] = Field(default=None, ge=0, le=2000)
    tag_ids: Optional[List[int]] = None


class TaskStatusUpdate(BaseModel):
    """Used by the Kanban board for fast drag-and-drop updates."""

    status: TaskStatus
    position: int = 0


class TaskOut(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    assigned_to: Optional[int] = None
    assignee: Optional[UserSummary] = None
    created_by: int
    creator: UserSummary
    parent_task_id: Optional[int] = None
    position: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    tags: List[TagOut] = Field(default_factory=list)
    comment_count: int = 0
    attachment_count: int = 0
    subtask_count: int = 0
    is_overdue: bool = False


class TaskBoardItem(BaseModel):
    """Compact shape used by the Kanban board endpoint, grouped by status."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    priority: TaskPriority
    status: TaskStatus
    due_date: Optional[datetime] = None
    assignee: Optional[UserSummary] = None
    position: int
    tags: List[TagOut] = Field(default_factory=list)
    comment_count: int = 0
    is_overdue: bool = False


class KanbanBoard(BaseModel):
    todo: List[TaskBoardItem]
    in_progress: List[TaskBoardItem]
    review: List[TaskBoardItem]
    completed: List[TaskBoardItem]
