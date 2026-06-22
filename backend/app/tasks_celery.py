import asyncio
from datetime import datetime, timedelta, timezone

from app.celery_app import celery_app
from app.database.db import SessionLocal
from app.models.audit_log import AuditLog
from app.models.notification import NotificationType
from app.models.task import Task, TaskStatus
from app.services.email_service import send_deadline_reminder_email
from app.services.notification_service import create_notification


@celery_app.task(name="app.tasks_celery.send_deadline_reminders")
def send_deadline_reminders():
    """
    Finds tasks due within the next 24 hours that are not yet completed and
    haven't already had a reminder sent, then notifies the assignee both
    in-app and by email. Scheduled hourly via Celery beat (see celery_app.py).
    """
    db = SessionLocal()
    sent = 0
    try:
        now = datetime.now(timezone.utc)
        window_end = now + timedelta(hours=24)
        candidates = (
            db.query(Task)
            .filter(
                Task.status != TaskStatus.COMPLETED,
                Task.due_date.isnot(None),
                Task.due_date >= now,
                Task.due_date <= window_end,
                Task.assigned_to.isnot(None),
            )
            .all()
        )

        for task in candidates:
            already_sent = (
                db.query(AuditLog)
                .filter(
                    AuditLog.action == "task.deadline_reminder_sent",
                    AuditLog.entity_id == task.id,
                    AuditLog.created_at >= now - timedelta(hours=24),
                )
                .first()
            )
            if already_sent:
                continue

            assignee = task.assignee
            if not assignee:
                continue

            asyncio.run(
                create_notification(
                    db,
                    user_id=assignee.id,
                    message=f"'{task.title}' is due on {task.due_date.strftime('%Y-%m-%d %H:%M')}",
                    notif_type=NotificationType.DEADLINE_REMINDER,
                    link=f"/projects/{task.project_id}/tasks/{task.id}",
                )
            )
            send_deadline_reminder_email(assignee.email, task.title, task.due_date.strftime("%Y-%m-%d %H:%M"))

            db.add(AuditLog(action="task.deadline_reminder_sent", entity_type="task", entity_id=task.id))
            db.commit()
            sent += 1
    finally:
        db.close()

    return {"reminders_sent": sent}
