from typing import List, Optional

from pydantic import BaseModel


class PrioritySuggestion(BaseModel):
    suggested_priority: str
    confidence: float
    reasoning: str


class DeadlinePrediction(BaseModel):
    task_id: int
    predicted_completion_date: Optional[str] = None
    basis: str


class WorkloadEntry(BaseModel):
    user_id: int
    username: str
    open_task_count: int
    overdue_count: int
    load_score: float
    recommendation: Optional[str] = None


class WorkloadDistribution(BaseModel):
    project_id: int
    entries: List[WorkloadEntry]
    most_loaded_user: Optional[str] = None
    least_loaded_user: Optional[str] = None


class ProjectInsight(BaseModel):
    project_id: int
    summary: from typing import List, Optional

from pydantic import BaseModel


class PrioritySuggestion(BaseModel):
    suggested_priority: str
    confidence: float
    reasoning: str


class DeadlinePrediction(BaseModel):
    task_id: int
    predicted_completion_date: Optional[str] = None
    basis: str


class WorkloadEntry(BaseModel):
    user_id: int
    username: str
    open_task_count: int
    overdue_count: int
    load_score: float
    recommendation: Optional[str] = None


class WorkloadDistribution(BaseModel):
    project_id: int
    entries: List[WorkloadEntry]
    most_loaded_user: Optional[str] = None
    least_loaded_user: Optional[str] = None


class ProjectInsight(BaseModel):
    project_id: int
    summary: str
    highlights: List[str]
    generated_by: Literals["heurustic", "anthropic"] # "heuristic" | "anthropic"


class TaskSummary(BaseModel):
    task_id: int
    summary: str
    generated_by: str
    highlights: List[str]
    generated_by: Literals["heuristic", "anthropic"]


class TaskSummary(BaseModel):
    task_id: int
    summary: str
    generated_by: Literals["heuristic", "anthropic"]
