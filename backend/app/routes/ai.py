from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import get_current_user, is_project_member_or_admin
from app.database.db import get_db
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.ai import DeadlinePrediction, PrioritySuggestion, ProjectInsight, TaskSummary, WorkloadDistribution
from app.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI Features"])


@router.post("/suggest-priority", response_model=PrioritySuggestion)
def suggest_priority(
    title: str = Body(...),
    description: Optional[str] = Body(default=None),
    due_date: Optional[datetime] = Body(default=None),
    current_user: User = Depends(get_current_user),
):
    return ai_service.suggest_priority(title, description, due_date)


@router.get("/predict-deadline/{task_id}", response_model=DeadlinePrediction)
def predict_deadline(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")
    result = ai_service.predict_deadline(db, task)
    return DeadlinePrediction(task_id=task.id, **result)


@router.get("/workload-distribution/{project_id}", response_model=WorkloadDistribution)
def workload_distribution(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not is_project_member_or_admin(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this project.")
    return ai_service.workload_distribution(db, project_id, project.members)


@router.get("/project-insights/{project_id}", response_model=ProjectInsight)
def project_insights(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not is_project_member_or_admin(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this project.")
    return ai_service.project_insight(db, project)


@router.post("/summarize-task/{task_id}", response_model=TaskSummary)
def summarize_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")
    return ai_service.summarize_task(task)
