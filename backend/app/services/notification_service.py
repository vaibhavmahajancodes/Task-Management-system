import re
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services.websocket_manager import manager

MENTION_PATTERN = re.compile(r"@([A-Za-z0-9_]{3,50})")


def extract_mentions(content: str) -> List[str]:
    """Returns the list of unique usernames referenced via @username in a comment."""
    seen = []
    for match in MENTION_PATTERN.findall(content):
        if match not in seen:
            seen.append(match)
    return seen


async def create_notification(
    db: Session,
    user_id: int,
    message: str,
    notif_type: NotificationType,
    link: Optional[str] = None,
) -> Notification:
    notif = Notification(user_id=user_id, message=message, notif_type=notif_type, link=link)
    db.add(notif)
    db.commit()
    db.refresh(notif)

    await manager.send_to_user(
        user_id,
        {
            "event": "notification",
            "data": {
                "id": notif.id,
                "message": notif.message,
                "notif_type": notif.notif_type.value,
                "link": notif.link,
                "is_read": notif.is_read,
                "created_at": notif.created_at.isoformat(),
            },
        },
    )
    return notif


async def notify_task_assigned(db: Session, task, assignee_id: int, actor_username: str) -> None:
    if assignee_id is None:
        return
    await create_notification(
        db,
        user_id=assignee_id,
        message=f"{actor_username} assigned you to '{task.title}'",
        notif_type=NotificationType.TASK_ASSIGNED,
        link=f"/projects/{task.project_id}/tasks/{task.id}",
    )


async def notify_mentions(db: Session, content: str, task, actor_username: str, exclude_user_id: int) -> None:
    usernames = extract_mentions(content)
    if not usernames:
        return
    mentioned_users = db.query(User).filter(User.username.in_(usernames)).all()
    for user in mentioned_users:
        if user.id == exclude_user_id:
            continue
        await create_notification(
            db,
            user_id=user.id,
            message=f"{actor_username} mentioned you on '{task.title}'",
            notif_type=NotificationType.MENTION,
            link=f"/projects/{task.project_id}/tasks/{task.id}",
        )


async def notify_comment(db: Session, task, actor_username: str, actor_id: int) -> None:
    """Notify the task assignee (if different from the commenter) that a new comment was posted."""
    if task.assigned_to and task.assigned_to != actor_id:
        await create_notification(
            db,
            user_id=task.assigned_to,
            message=f"{actor_username} commented on '{task.title}'",
            notif_type=NotificationType.COMMENT,
            link=f"/projects/{task.project_id}/tasks/{task.id}",
        )


async def broadcast_task_event(project_id: int, event: str, task_data: dict) -> None:
    """Pushes a live update to everyone currently viewing this project's Kanban board."""
    await manager.broadcast_to_project(project_id, {"event": event, "data": task_data})
