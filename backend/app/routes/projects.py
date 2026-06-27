from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import can_manage_project, get_current_user, is_project_member_or_admin, require_role
from app.database.db import get_db
from app.models.notification import NotificationType
from app.models.project import Project, ProjectPriority, ProjectStatus
from app.models.task import Task, TaskStatus
from app.models.user import User, UserRole
from app.schemas.common import Message
from app.schemas.project import ProjectCreate, ProjectListItem, ProjectMemberUpdate, ProjectOut, ProjectUpdate
from app.services.audit_service import log_action
from app.services.notification_service import create_notification

router = APIRouter(prefix="/projects", tags=["Projects"])

_MAX_SEARCH_LEN  = 100  

def _project_query(db: Session):
    return db.query(Project).options(joinedload(Project.owner), joinedload(Project.members))


def _to_project_out(db: Session, project: Project) -> ProjectOut:
    total = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
    completed = (
        db.query(func.count(Task.id))
        .filter(Task.project_id == project.id, Task.status == TaskStatus.COMPLETED)
        .scalar()
        or 0
    )
    out = ProjectOut.model_validate(project)
    out.task_count = total
    out.completed_task_count = completed
    out.progress_percent = round((completed / total) * 100, 1) if total else 0.0
    return out


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.PROJECT_MANAGER)),
):
    project = Project(
        name=payload.name,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        deadline=payload.deadline,
        color=payload.color,
        owner_id=current_user.id,
    )
    if payload.member_ids:
        members = db.query(User).filter(User.id.in_(payload.member_ids)).all()
        project.members = members
    db.add(project)
    db.commit()
    db.refresh(project)

    log_action(db, current_user.id, "project.created", "project", project.id, f"Created project '{project.name}'")
    return _to_project_out(db, project)


@router.get("", response_model=List[ProjectListItem])
def list_projects(
    status_filter: Optional[ProjectStatus] = Query(default=None, alias="status"),
    priority: Optional[ProjectPriority] = None,
    search: Optional[str] = None,
    include_archived: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _project_query(db)

    if current_user.role != UserRole.ADMIN:
        query = query.filter(
            (Project.owner_id == current_user.id) | (Project.members.any(User.id == current_user.id))
        )
    if not include_archived:
        query = query.filter(Project.is_archived.is_(False))
    if status_filter:
        query = query.filter(Project.status == status_filter)
    if priority:
        query = query.filter(Project.priority == priority)
    if search:
        query = query.filter(Project.name.ilike(f"%{search}%"))

    projects = query.order_by(Project.created_at.desc()).all()
    results = []
    for project in projects:
        out = _to_project_out(db, project)
        results.append(
            ProjectListItem(
                id=project.id,
                name=project.name,
                status=project.status,
                priority=project.priority,
                deadline=project.deadline,
                color=project.color,
                is_archived=project.is_archived,
                progress_percent=out.progress_percent,
                task_count=out.task_count,
            )
        )
    return results


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = _project_query(db).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not is_project_member_or_admin(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this project.")
    return _to_project_out(db, project)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_query(db).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not can_manage_project(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to edit this project.")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)

    log_action(db, current_user.id, "project.updated", "project", project.id)
    return _to_project_out(db, project)


@router.delete("/{project_id}", response_model=Message)
def delete_project(
    project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if current_user.role != UserRole.ADMIN and project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the owner or an admin can delete this project.")

    name = project.name
    db.delete(project)
    db.commit()
    log_action(db, current_user.id, "project.deleted", "project", project_id, f"Deleted project '{name}'")
    return Message(message=f"Project '{name}' deleted.")


@router.post("/{project_id}/archive", response_model=ProjectOut)
def archive_project(
    project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    project = _project_query(db).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not can_manage_project(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to archive this project.")
    project.is_archived = True
    project.status = ProjectStatus.ARCHIVED
    db.commit()
    db.refresh(project)
    log_action(db, current_user.id, "project.archived", "project", project.id)
    return _to_project_out(db, project)


@router.post("/{project_id}/restore", response_model=ProjectOut)
def restore_project(
    project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    project = _project_query(db).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not can_manage_project(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to restore this project.")
    project.is_archived = False
    project.status = ProjectStatus.ACTIVE
    db.commit()
    db.refresh(project)
    log_action(db, current_user.id, "project.restored", "project", project.id)
    return _to_project_out(db, project)


@router.post("/{project_id}/members", response_model=ProjectOut)
async def add_project_member(
    project_id: int,
    payload: ProjectMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_query(db).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not can_manage_project(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to manage members.")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if user not in project.members:
        project.members.append(user)
        db.commit()
        db.refresh(project)
        await create_notification(
            db,
            user_id=user.id,
            message=f"You were added to the project '{project.name}'",
            notif_type=NotificationType.PROJECT_INVITE,
            link=f"/projects/{project.id}",
        )
        log_action(db, current_user.id, "project.member_added", "project", project.id, f"Added user {user.username}")
    return _to_project_out(db, project)


@router.delete("/{project_id}/members/{user_id}", response_model=ProjectOut)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _project_query(db).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not can_manage_project(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have permission to manage members.")

    project.members = [m for m in project.members if m.id != user_id]
    db.commit()
    db.refresh(project)
    log_action(db, current_user.id, "project.member_removed", "project", project.id, f"Removed user id {user_id}")
    return _to_project_out(db, project)
