from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth.permissions import get_current_user, is_project_member_or_admin
from app.database.db import get_db
from app.models.task import Task
from app.models.time_log import TimeLog
from app.models.user import User
from app.schemas.time_log import TimeLogOut, TimeLogStart, TimesheetEntry

router = APIRouter(prefix="/time-logs", tags=["Time Tracking"])


@router.post("/start", response_model=TimeLogOut, status_code=201)
def start_timer(payload: TimeLogStart, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == payload.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")

    running = (
        db.query(TimeLog)
        .filter(TimeLog.user_id == current_user.id, TimeLog.end_time.is_(None))
        .first()
    )
    if running:
        raise HTTPException(
            status_code=400,
            detail=f"You already have a running timer on task #{running.task_id}. Stop it before starting another.",
        )

    log = TimeLog(task_id=payload.task_id, user_id=current_user.id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.post("/{log_id}/stop", response_model=TimeLogOut)
def stop_timer(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(TimeLog).filter(TimeLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Time log not found.")
    if log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only stop your own timer.")
    if log.end_time is not None:
        raise HTTPException(status_code=400, detail="This timer has already been stopped.")

    log.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(log)
    return log


@router.get("/running", response_model=Optional[TimeLogOut])
def get_running_timer(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = (
        db.query(TimeLog)
        .filter(TimeLog.user_id == current_user.id, TimeLog.end_time.is_(None))
        .first()
    )
    return log


@router.get("/task/{task_id}", response_model=List[TimeLogOut])
def list_task_time_logs(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    if not is_project_member_or_admin(task.project, current_user):
        raise HTTPException(status_code=403, detail="You do not have access to this task.")
    return (
        db.query(TimeLog)
        .options(joinedload(TimeLog.user))
        .filter(TimeLog.task_id == task_id)
        .order_by(TimeLog.start_time.desc())
        .all()
    )


@router.get("/timesheet", response_model=List[TimesheetEntry])
def timesheet_report(
    project_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = db.query(TimeLog).options(joinedload(TimeLog.user), joinedload(TimeLog.task)).filter(
        TimeLog.end_time.isnot(None)
    )
    if project_id:
        query = query.join(Task).filter(Task.project_id == project_id)

    logs = query.all()
    totals: dict = {}
    for log in logs:
        bucket = totals.setdefault(log.user_id, {"user": log.user, "total_seconds": 0, "entry_count": 0})
        bucket["total_seconds"] += log.duration_seconds
        bucket["entry_count"] += 1

    return [
        TimesheetEntry(user=v["user"], total_seconds=v["total_seconds"], entry_count=v["entry_count"])
        for v in sorted(totals.values(), key=lambda v: v["total_seconds"], reverse=True)
    ]
