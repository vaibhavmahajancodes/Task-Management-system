import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import get_current_user, is_project_member_or_admin
from app.config import settings
from app.database.db import get_db
from app.models.attachment import Attachment
from app.models.project import Project
from app.models.task import Task
from app.models.user import User
from app.schemas.attachment import AttachmentOut
from app.schemas.common import Message
from app.services.audit_service import log_action

router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_ROOT = settings.UPLOAD_DIR


def _to_out(attachment: Attachment) -> AttachmentOut:
    out = AttachmentOut.model_validate(attachment)
    out.download_url = f"{settings.API_PREFIX}/files/{attachment.id}/download"
    return out


def _ensure_project_access(db: Session, current_user: User, task_id: Optional[int], project_id: Optional[int]):
    if task_id:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")
        if not is_project_member_or_admin(task.project, current_user):
            raise HTTPException(status_code=403, detail="You do not have access to this task.")
        return task.project_id
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
        if not is_project_member_or_admin(project, current_user):
            raise HTTPException(status_code=403, detail="You do not have access to this project.")
        return project_id
    raise HTTPException(status_code=400, detail="Either task_id or project_id is required.")


@router.post("/upload", response_model=AttachmentOut, status_code=201)
async def upload_file(
    task_id: Optional[int] = None,
    project_id: Optional[int] = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resolved_project_id = _ensure_project_access(db, current_user, task_id, project_id)

    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in settings.allowed_upload_extensions_list:
        raise HTTPException(status_code=400, detail=f"File type '{extension}' is not allowed.")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File exceeds the {settings.MAX_UPLOAD_SIZE_MB}MB limit.")

    sub_dir = f"project_{resolved_project_id}"
    target_dir = os.path.join(UPLOAD_ROOT, sub_dir)
    os.makedirs(target_dir, exist_ok=True)

    stored_name = f"{uuid.uuid4().hex}{extension}"
    full_path = os.path.join(target_dir, stored_name)
    with open(full_path, "wb") as f:
        f.write(contents)

    attachment = Attachment(
        file_name=stored_name,
        original_name=file.filename or stored_name,
        file_path=full_path,
        file_size=len(contents),
        content_type=file.content_type,
        task_id=task_id,
        project_id=project_id,
        uploaded_by=current_user.id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    log_action(db, current_user.id, "file.uploaded", "attachment", attachment.id, attachment.original_name)
    attachment = (
        db.query(Attachment).options(joinedload(Attachment.uploader)).filter(Attachment.id == attachment.id).first()
    )
    return _to_out(attachment)


@router.get("/task/{task_id}", response_model=List[AttachmentOut])
def list_task_attachments(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")
    attachments = (
        db.query(Attachment)
        .options(joinedload(Attachment.uploader))
        .filter(Attachment.task_id == task_id)
        .order_by(Attachment.created_at.desc())
        .all()
    )
    return [_to_out(a) for a in attachments]


@router.get("/project/{project_id}", response_model=List[AttachmentOut])
def list_project_attachments(
    project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    if not is_project_member_or_admin(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this project.")
    attachments = (
        db.query(Attachment)
        .options(joinedload(Attachment.uploader))
        .filter(Attachment.project_id == project_id)
        .order_by(Attachment.created_at.desc())
        .all()
    )
    return [_to_out(a) for a in attachments]


@router.get("/{attachment_id}/download")
def download_file(attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="File not found.")

    resolved_project_id = attachment.project_id
    if attachment.task_id:
        task = db.query(Task).filter(Task.id == attachment.task_id).first()
        resolved_project_id = task.project_id if task else None
    project = db.query(Project).filter(Project.id == resolved_project_id).first() if resolved_project_id else None
    if not project or not is_project_member_or_admin(project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this file.")

    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=404, detail="File is missing from storage.")

    return FileResponse(
        attachment.file_path, filename=attachment.original_name, media_type=attachment.content_type
    )


@router.delete("/{attachment_id}", response_model=Message)
def delete_attachment(
    attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="File not found.")
    if attachment.uploaded_by != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="You can only delete files you uploaded.")

    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)
    db.delete(attachment)
    db.commit()
    log_action(db, current_user.id, "file.deleted", "attachment", attachment_id)
    return Message(message="File deleted.")
