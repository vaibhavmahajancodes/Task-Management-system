from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import get_current_user
from app.database.db import get_db
from app.models.project import Project
from app.models.task import Task
from app.models.user import User, UserRole
from app.schemas.task import TaskOut
from app.routes.tasks import _to_task_out

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("/tasks", response_model=List[TaskOut])
def get_calendar_tasks(
    start: datetime = Query(..., description="Range start (inclusive)"),
    end: datetime = Query(..., description="Range end (inclusive)"),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns every task with a due date inside [start, end], for month/week/day calendar views."""
    query = (
        db.query(Task)
        .options(joinedload(Task.assignee), joinedload(Task.creator), joinedload(Task.tags))
        .join(Project, Task.project_id == Project.id)
        .filter(Task.due_date.isnot(None), Task.due_date >= start, Task.due_date <= end)
    )
    if current_user.role != UserRole.ADMIN:
        query = query.filter(
            (Project.owner_id == current_user.id) | (Project.members.any(User.id == current_user.id))
        )
    if project_id:
        query = query.filter(Task.project_id == project_id)

    tasks = query.order_by(Task.due_date.asc()).all()
    return [_to_task_out(db, t) for t in tasks]
