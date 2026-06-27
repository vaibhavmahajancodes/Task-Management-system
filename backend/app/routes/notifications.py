from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.permissions import get_current_user
from app.database.db import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import Message
from app.schemas.notification import NotificationOut, UnreadCount

router = APIRouter(prefix="/notifications", tags=["Notifications"])

_DEFAULT_LIMIT = 50
_MAX_LIMIT     = 200

@router.get("", response_model=List["NotificationOut"])
def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    return query.order_by(Notification.created_at.desc()).limit(limit).all()


@router.get("/unread-count", response_model=UnreadCount)
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .count()
    )
    return UnreadCount(unread_count=count)


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/read-all", response_model=Message)
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False)).update(
        {"is_read": True}
    )
    db.commit()
    return Message(message="All notifications marked as read.")


@router.delete("/{notification_id}", response_model=Message)
def delete_notification(
    notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    db.delete(notif)
    db.commit()
    return Message(message="Notification deleted.")
