from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func, false
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import get_current_user
from app.database.db import get_db
from app.models.audit_log import AuditLog
from app.models.project import Project, ProjectStatus
from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole
from app.schemas.report import ActivityItem, DashboardSummary, ProjectProgressItem, TeamPerformanceItem

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _visible_project_ids(db: Session, current_user: User) -> List[int]:
    query = db.query(Project.id)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(
            (Project.owner_id == current_user.id) | (Project.members.any(User.id == current_user.id))
        )
    return [row[0] for row in query.all()]


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_ids = _visible_project_ids(db, current_user)
    now = datetime.now(timezone.utc)
    week_from_now = now + timedelta(days=7)

    total_projects = len(project_ids)
    active_projects = (
        db.query(func.count(Project.id))
        .filter(Project.id.in_(project_ids), Project.status == ProjectStatus.ACTIVE)
        .scalar()
        or 0
    )

    task_base = db.query(Task).filter(Task.project_id.in_(project_ids)) if project_ids else db.query(Task).filter(false())
    total_tasks = task_base.count()
    completed_tasks = task_base.filter(Task.status == TaskStatus.COMPLETED).count()
    pending_tasks = task_base.filter(Task.status != TaskStatus.COMPLETED).count()
    overdue_tasks = task_base.filter(
        Task.status != TaskStatus.COMPLETED, Task.due_date.isnot(None), Task.due_date < now
    ).count()
    due_this_week = task_base.filter(
        Task.status != TaskStatus.COMPLETED,
        Task.due_date.isnot(None),
        Task.due_date >= now,
        Task.due_date <= week_from_now,
    ).count()

    return DashboardSummary(
        total_projects=total_projects,
        active_projects=active_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        tasks_due_this_week=due_this_week,
        completion_rate=round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0.0,
    )


@router.get("/recent-activity", response_model=List[ActivityItem])
def get_recent_activity(limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(AuditLog).options(joinedload(AuditLog.user))
    if current_user.role != UserRole.ADMIN:
        query = query.filter(AuditLog.user_id == current_user.id)
    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
    return [
        ActivityItem(
            id=log.id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            username=log.user.username if log.user else None,
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.get("/team-performance", response_model=List[TeamPerformanceItem])
def get_team_performance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_ids = _visible_project_ids(db, current_user)
    if not project_ids:
        return []
    now = datetime.now(timezone.utc)

    users = db.query(User).filter(User.is_active.is_(True)).all()
    results = []
    for user in users:
        assigned = (
            db.query(Task)
            .filter(Task.project_id.in_(project_ids), Task.assigned_to == user.id)
            .all()
        )
        if not assigned:
            continue
        completed = sum(1 for t in assigned if t.status == TaskStatus.COMPLETED)
        overdue = sum(
            1
            for t in assigned
            if t.status != TaskStatus.COMPLETED and t.due_date and t.due_date < now
        )
        results.append(
            TeamPerformanceItem(
                user_id=user.id,
                username=user.username,
                full_name=user.full_name,
                assigned_count=len(assigned),
                completed_count=completed,
                overdue_count=overdue,
                completion_rate=round((completed / len(assigned)) * 100, 1) if assigned else 0.0,
            )
        )
    return sorted(results, key=lambda r: r.completion_rate, reverse=True)


@router.get("/project-progress", response_model=List[ProjectProgressItem])
def get_project_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project_ids = _visible_project_ids(db, current_user)
    if not project_ids:
        return []
    today = datetime.now(timezone.utc).date()

    projects = db.query(Project).filter(Project.id.in_(project_ids), Project.is_archived.is_(False)).all()
    results = []
    for project in projects:
        total = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
        completed = (
            db.query(func.count(Task.id))
            .filter(Task.project_id == project.id, Task.status == TaskStatus.COMPLETED)
            .scalar()
            or 0
        )
        results.append(
            ProjectProgressItem(
                project_id=project.id,
                project_name=project.name,
                color=project.color,
                total_tasks=total,
                completed_tasks=completed,
                progress_percent=round((completed / total) * 100, 1) if total else 0.0,
                deadline=project.deadline.isoformat() if project.deadline else None,
                is_overdue=bool(project.deadline and project.deadline < today and completed < total),
            )
        )
    return results
