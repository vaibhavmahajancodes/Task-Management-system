from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_projects: int
    active_projects: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    tasks_due_this_week: int
    completion_rate: float


class TeamPerformanceItem(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str] = None
    assigned_count: int
    completed_count: int
    overdue_count: int
    completion_rate: float


class ProjectProgressItem(BaseModel):
    project_id: int
    project_name: str
    color: str
    total_tasks: int
    completed_tasks: int
    progress_percent: float
    deadline: Optional[datetime]
    is_overdue: bool


class ActivityItem(BaseModel):
    id: int
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    username: Optional[str] = None
    created_at: datetime


class TaskCompletionReport(BaseModel):
    period: str
    completed: int
    created: int


class DeadlineAnalysisItem(BaseModel):
    project_id: int
    project_name: str
    on_time: int
    overdue: int
    upcoming: int


class ReportBundle(BaseModel):
    """Aggregated payload used to render the in-app Reports page."""

    task_completion: List[TaskCompletionReport]
    team_productivity: List[TeamPerformanceItem]
    project_progress: List[ProjectProgressItem]
    deadline_analysis: List[DeadlineAnalysisItem]
