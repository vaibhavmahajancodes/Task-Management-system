from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import get_current_user, is_project_member_or_admin
from app.database.db import get_db
from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut, CommentUpdate
from app.schemas.common import Message
from app.services.audit_service import log_action
from app.services.notification_service import broadcast_task_event, extract_mentions, notify_comment, notify_mentions

router = APIRouter(tags=["Comments"])


def _to_comment_out(comment: Comment) -> CommentOut:
    out = CommentOut.model_validate(comment)
    out.mentioned_usernames = extract_mentions(comment.content)
    return out


@router.post("/tasks/{task_id}/comments", response_model=CommentOut, status_code=201)
async def create_comment(
    task_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")

    comment = Comment(content=payload.content, user_id=current_user.id, task_id=task_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    await notify_comment(db, task, current_user.username, current_user.id)
    await notify_mentions(db, payload.content, task, current_user.username, current_user.id)
    await broadcast_task_event(task.project_id, "comment_added", {"task_id": task.id, "comment_id": comment.id})
    log_action(db, current_user.id, "comment.created", "task", task.id)

    comment = db.query(Comment).options(joinedload(Comment.user)).filter(Comment.id == comment.id).first()
    return _to_comment_out(comment)


@router.get("/tasks/{task_id}/comments", response_model=List[CommentOut])
def list_comments(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")

    comments = (
        db.query(Comment)
        .options(joinedload(Comment.user))
        .filter(Comment.task_id == task_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [_to_comment_out(c) for c in comments]


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).options(joinedload(Comment.user)).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")
    if comment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="You can only edit your own comments.")

    comment.content = payload.content
    db.commit()
    db.refresh(comment)
    return _to_comment_out(comment)


@router.delete("/comments/{comment_id}", response_model=Message)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")
    if comment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="You can only delete your own comments.")

    db.delete(comment)
    db.commit()
    return Message(message="Comment deleted.")
