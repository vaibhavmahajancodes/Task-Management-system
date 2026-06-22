import math
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import get_current_user, is_project_member_or_admin
from app.database.db import get_db
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.project import Project
from app.models.tag import Tag
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User, UserRole
from app.schemas.common import Message, Page
from app.schemas.task import KanbanBoard, TaskBoardItem, TaskCreate, TaskOut, TaskStatusUpdate, TaskUpdate
from app.services.audit_service import log_action
from app.services.notification_service import broadcast_task_event, notify_task_assigned

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _task_query(db: Session):
    return db.query(Task).options(
        joinedload(Task.assignee), joinedload(Task.creator), joinedload(Task.tags)
    )


def _get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


def _to_task_out(db: Session, task: Task) -> TaskOut:
    comment_count = db.query(func.count(Comment.id)).filter(Comment.task_id == task.id).scalar() or 0
    attachment_count = db.query(func.count(Attachment.id)).filter(Attachment.task_id == task.id).scalar() or 0
    subtask_count = db.query(func.count(Task.id)).filter(Task.parent_task_id == task.id).scalar() or 0
    out = TaskOut.model_validate(task)
    out.comment_count = comment_count
    out.attachment_count = attachment_count
    out.subtask_count = subtask_count
    out.is_overdue = bool(
        task.due_date
        and task.status != TaskStatus.COMPLETED
        and task.due_date.replace(tzinfo=task.due_date.tzinfo or timezone.utc) < datetime.now(timezone.utc)
    )
    return out


def _to_board_item(task: Task) -> TaskBoardItem:
    item = TaskBoardItem.model_validate(task)
    item.is_overdue = bool(
        task.due_date
        and task.status != TaskStatus.COMPLETED
        and task.due_date.replace(tzinfo=task.due_date.tzinfo or timezone.utc) < datetime.now(timezone.utc)
    )
    item.comment_count = len(task.comments) if task.comments is not None else 0
    return item


@router.post("", response_model=TaskOut, status_code=201)
async def create_task(
    payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    project = _get_project_or_404(db, payload.project_id)
    if not is_project_member_or_admin(project, current_user):
        raise HTTPException(status_code=403, detail="You are not a member of this project.")

    max_position = (
        db.query(func.max(Task.position))
        .filter(Task.project_id == payload.project_id, Task.status == payload.status)
        .scalar()
    )

    task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        estimated_hours=payload.estimated_hours,
        project_id=payload.project_id,
        assigned_to=payload.assigned_to,
        parent_task_id=payload.parent_task_id,
        created_by=current_user.id,
        position=(max_position + 1) if max_position is not None else 0,
    )
    if payload.tag_ids:
        task.tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()

    db.add(task)
    db.commit()
    db.refresh(task)

    log_action(db, current_user.id, "task.created", "task", task.id, f"Created task '{task.title}'")
    if task.assigned_to:
        await notify_task_assigned(db, task, task.assigned_to, current_user.username)
    await broadcast_task_event(task.project_id, "task_created", {"id": task.id, "status": task.status.value})

    return _to_task_out(db, task)


@router.get("", response_model=Page[TaskOut])
def list_tasks(
    project_id: Optional[int] = None,
    status_filter: Optional[TaskStatus] = Query(default=None, alias="status"),
    priority: Optional[TaskPriority] = None,
    assigned_to: Optional[int] = None,
    tag_id: Optional[int] = None,
    search: Optional[str] = None,
    due_before: Optional[datetime] = None,
    due_after: Optional[datetime] = None,
    sort_by: str = Query(default="created_at", pattern="^(created_at|due_date|priority|title|status)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _task_query(db).join(Project, Task.project_id == Project.id)

    if current_user.role != UserRole.ADMIN:
        query = query.filter(
            (Project.owner_id == current_user.id) | (Project.members.any(User.id == current_user.id))
        )

    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority:
        query = query.filter(Task.priority == priority)
    if assigned_to:
        query = query.filter(Task.assigned_to == assigned_to)
    if tag_id:
        query = query.filter(Task.tags.any(Tag.id == tag_id))
    if search:
        query = query.filter(or_(Task.title.ilike(f"%{search}%"), Task.description.ilike(f"%{search}%")))
    if due_before:
        query = query.filter(Task.due_date <= due_before)
    if due_after:
        query = query.filter(Task.due_date >= due_after)

    sort_column = getattr(Task, sort_by)
    query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

    total = query.count()
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()

    return Page(
        items=[_to_task_out(db, t) for t in tasks],
        total=total,
        page=page,
        page_size=page_size,
        pages=max(1, math.ceil(total / page_size)),
    )


@router.get("/board/{project_id}", response_model=KanbanBoard)
def get_kanban_board(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = _get_project_or_404(db, project_id)
    if not is_project_member_or_admin(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this project.")

    tasks = (
        _task_query(db)
        .filter(Task.project_id == project_id)
        .order_by(Task.position.asc())
        .all()
    )
    board = {status.value: [] for status in TaskStatus}
    for task in tasks:
        board[task.status.value].append(_to_board_item(task))

    return KanbanBoard(
        todo=board[TaskStatus.TODO.value],
        in_progress=board[TaskStatus.IN_PROGRESS.value],
        review=board[TaskStatus.REVIEW.value],
        completed=board[TaskStatus.COMPLETED.value],
    )


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = _task_query(db).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")
    return _to_task_out(db, task)


@router.put("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    task = _task_query(db).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")

    data = payload.model_dump(exclude_unset=True, exclude={"tag_ids"})
    previous_assignee = task.assigned_to
    previous_status = task.status

    for field, value in data.items():
        setattr(task, field, value)

    if payload.tag_ids is not None:
        task.tags = db.query(Tag).filter(Tag.id.in_(payload.tag_ids)).all()

    if task.status == TaskStatus.COMPLETED and previous_status != TaskStatus.COMPLETED:
        task.completed_at = datetime.now(timezone.utc)
    elif task.status != TaskStatus.COMPLETED:
        task.completed_at = None

    db.commit()
    db.refresh(task)

    log_action(db, current_user.id, "task.updated", "task", task.id)
    if task.assigned_to and task.assigned_to != previous_assignee:
        await notify_task_assigned(db, task, task.assigned_to, current_user.username)
    await broadcast_task_event(task.project_id, "task_updated", {"id": task.id, "status": task.status.value})

    return _to_task_out(db, task)


@router.patch("/{task_id}/status", response_model=TaskOut)
async def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fast-path endpoint used by the Kanban board's drag-and-drop interaction."""
    task = _task_query(db).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")

    previous_status = task.status
    task.status = payload.status
    task.position = payload.position
    if task.status == TaskStatus.COMPLETED and previous_status != TaskStatus.COMPLETED:
        task.completed_at = datetime.now(timezone.utc)
    elif task.status != TaskStatus.COMPLETED:
        task.completed_at = None

    db.commit()
    db.refresh(task)

    await broadcast_task_event(
        task.project_id,
        "task_moved",
        {"id": task.id, "status": task.status.value, "position": task.position},
    )
    return _to_task_out(db, task)


@router.delete("/{task_id}", response_model=Message)
async def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    project = db.query(Project).filter(Project.id == task.project_id).first()
    can_delete = (
        current_user.role == UserRole.ADMIN
        or task.created_by == current_user.id
        or (project and project.owner_id == current_user.id)
        or current_user.role == UserRole.PROJECT_MANAGER
    )
    if not can_delete:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this task.")

    project_id = task.project_id
    title = task.title
    db.delete(task)
    db.commit()

    log_action(db, current_user.id, "task.deleted", "task", task_id, f"Deleted task '{title}'")
    await broadcast_task_event(project_id, "task_deleted", {"id": task_id})
    return Message(message=f"Task '{title}' deleted.")


@router.post("/{task_id}/subtasks", response_model=TaskOut, status_code=201)
async def create_subtask(
    task_id: int, payload: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    parent = db.query(Task).filter(Task.id == task_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent task not found.")
    if not is_project_member_or_admin(parent.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")

    subtask = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        estimated_hours=payload.estimated_hours,
        project_id=parent.project_id,
        assigned_to=payload.assigned_to,
        parent_task_id=parent.id,
        created_by=current_user.id,
    )
    db.add(subtask)
    db.commit()
    db.refresh(subtask)

    log_action(db, current_user.id, "task.subtask_created", "task", subtask.id, f"Subtask of task {parent.id}")
    if subtask.assigned_to:
        await notify_task_assigned(db, subtask, subtask.assigned_to, current_user.username)
    return _to_task_out(db, subtask)


@router.get("/{task_id}/subtasks", response_model=List[TaskOut])
def list_subtasks(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    parent = db.query(Task).filter(Task.id == task_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent task not found.")
    if not is_project_member_or_admin(parent.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")
    subtasks = _task_query(db).filter(Task.parent_task_id == task_id).all()
    return [_to_task_out(db, t) for t in subtasks]
