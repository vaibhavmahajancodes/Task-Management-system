from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy import false
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import get_current_user
from app.database.db import get_db
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole
from app.schemas.report import DeadlineAnalysisItem, TaskCompletionReport
from app.services.report_service import export_tasks_csv, export_tasks_excel, export_tasks_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])


def _visible_project_ids(db: Session, current_user: User) -> List[int]:
    query = db.query(Project.id)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(
            (Project.owner_id == current_user.id) | (Project.members.any(User.id == current_user.id))
        )
    return [row[0] for row in query.all()]


def _filtered_tasks(db: Session, current_user: User, project_id: Optional[int]):
    project_ids = _visible_project_ids(db, current_user)
    query = (
        db.query(Task)
        .options(joinedload(Task.project), joinedload(Task.assignee))
        .filter(Task.project_id.in_(project_ids) if project_ids else false())
    )
    if project_id:
        query = query.filter(Task.project_id == project_id)
    return query.order_by(Task.created_at.desc()).all()


@router.get("/task-completion", response_model=List[TaskCompletionReport])
def task_completion_report(
    weeks: int = 8, project_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Completed vs. created task counts for each of the last N weeks."""
    tasks = _filtered_tasks(db, current_user, project_id)
    now = datetime.now(timezone.utc)
    buckets = []
    for i in range(weeks - 1, -1, -1):
        week_start = now - timedelta(weeks=i + 1)
        week_end = now - timedelta(weeks=i)
        created = sum(1 for t in tasks if t.created_at and week_start <= t.created_at < week_end)
        completed = sum(1 for t in tasks if t.completed_at and week_start <= t.completed_at < week_end)
        buckets.append(
            TaskCompletionReport(period=week_start.strftime("%b %d"), completed=completed, created=created)
        )
    return buckets


@router.get("/deadline-analysis", response_model=List[DeadlineAnalysisItem])
def deadline_analysis(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_ids = _visible_project_ids(db, current_user)
    now = datetime.now(timezone.utc)
    results = []
    projects = db.query(Project).filter(Project.id.in_(project_ids)) if project_ids else []
    for project in projects:
        tasks = db.query(Task).filter(Task.project_id == project.id, Task.due_date.isnot(None)).all()
        on_time = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED and t.completed_at and t.completed_at <= t.due_date)
        overdue = sum(1 for t in tasks if t.status != TaskStatus.COMPLETED and t.due_date < now)
        upcoming = sum(1 for t in tasks if t.status != TaskStatus.COMPLETED and t.due_date >= now)
        results.append(
            DeadlineAnalysisItem(
                project_id=project.id, project_name=project.name, on_time=on_time, overdue=overdue, upcoming=upcoming
            )
        )
    return results


@router.get("/export/csv")
def export_csv(project_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = _filtered_tasks(db, current_user, project_id)
    content = export_tasks_csv(tasks)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=task_report.csv"},
    )


@router.get("/export/excel")
def export_excel(project_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = _filtered_tasks(db, current_user, project_id)
    content = export_tasks_excel(tasks)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=task_report.xlsx"},
    )


@router.get("/export/pdf")
def export_pdf(project_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = _filtered_tasks(db, current_user, project_id)
    content = export_tasks_pdf(tasks)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=task_report.pdf"},
    )
