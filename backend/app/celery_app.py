"""
Celery worker entry point. Run with:
    celery -A app.celery_app worker --loglevel=info
    celery -A app.celery_app beat --loglevel=info   # for the scheduled deadline-reminder job
"""
from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "taskmanager",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks_celery"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Runs once an hour, looking for tasks due within the next 24h that haven't
# already had a reminder sent (see app.tasks_celery.send_deadline_reminders).
celery_app.conf.beat_schedule = {
    "send-deadline-reminders-hourly": {
        "task": "app.tasks_celery.send_deadline_reminders",
        "schedule": crontab(minute=0, hour="*"),
    },
}
