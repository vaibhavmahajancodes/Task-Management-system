"""
AI-powered features.

These are implemented as transparent, explainable heuristics by default so
the app works fully offline and the "why" behind a suggestion is always
visible to the user. If `ANTHROPIC_API_KEY` is configured, the narrative
endpoints (project insights / task summarisation) additionally call the
Claude API for a richer, natural-language write-up, with the heuristic
output kept as the guaranteed fallback if that call fails or isn't configured.
"""
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.task import Task, TaskPriority, TaskStatus

URGENT_KEYWORDS = {"urgent", "asap", "blocker", "critical", "outage", "breaking", "production"}
HIGH_KEYWORDS = {"important", "deadline", "client", "release", "launch"}


def suggest_priority(title: str, description: Optional[str], due_date: Optional[datetime]) -> dict:
    text = f"{title} {description or ''}".lower()
    score = 0
    reasons = []

    if any(word in text for word in URGENT_KEYWORDS):
        score += 3
        reasons.append("language suggests urgency (e.g. 'urgent', 'blocker', 'critical')")
    elif any(word in text for word in HIGH_KEYWORDS):
        score += 2
        reasons.append("language suggests business importance (e.g. 'deadline', 'client', 'release')")

    if due_date:
        days_left = (due_date.replace(tzinfo=due_date.tzinfo or timezone.utc) - datetime.now(timezone.utc)).days
        if days_left <= 1:
            score += 3
            reasons.append("due date is within 24 hours")
        elif days_left <= 3:
            score += 2
            reasons.append("due date is within 3 days")
        elif days_left <= 7:
            score += 1
            reasons.append("due date is within a week")

    if score >= 5:
        priority = TaskPriority.CRITICAL
    elif score >= 3:
        priority = TaskPriority.HIGH
    elif score >= 1:
        priority = TaskPriority.MEDIUM
    else:
        priority = TaskPriority.LOW
        reasons.append("no urgency signals or near-term deadline detected")

    confidence = min(0.95, 0.5 + score * 0.1)
    return {
        "suggested_priority": priority.value,
        "confidence": round(confidence, 2),
        "reasoning": "; ".join(reasons),
    }


def predict_deadline(db: Session, task: Task) -> dict:
    """
    Estimates a completion date using the average historical turnaround time
    (created_at -> completed_at) for completed tasks of the same priority in
    the same project. Falls back to a sensible default if there isn't enough
    history yet.
    """
    completed = (
        db.query(Task)
        .filter(
            Task.project_id == task.project_id,
            Task.priority == task.priority,
            Task.status == TaskStatus.COMPLETED,
            Task.completed_at.isnot(None),
        )
        .limit(50)
        .all()
    )
    durations = [
        (t.completed_at - t.created_at).total_seconds() / 86400.0 for t in completed if t.completed_at and t.created_at
    ]
    if durations:
        avg_days = mean(durations)
        basis = f"based on the average of {len(durations)} completed {task.priority.value}-priority task(s) in this project"
    else:
        defaults = {
            TaskPriority.CRITICAL: 1,
            TaskPriority.HIGH: 3,
            TaskPriority.MEDIUM: 5,
            TaskPriority.LOW: 10,
        }
        avg_days = defaults.get(task.priority, 5)
        basis = "based on a default estimate (not enough historical data for this project yet)"

    predicted = (task.created_at or datetime.now(timezone.utc)) + timedelta(days=avg_days)
    return {"predicted_completion_date": predicted.date().isoformat(), "basis": basis}


def workload_distribution(db: Session, project_id: int, members: List) -> dict:
    entries = []
    now = datetime.now(timezone.utc)
    for member in members:
        open_tasks = (
            db.query(Task)
            .filter(
                Task.project_id == project_id,
                Task.assigned_to == member.id,
                Task.status != TaskStatus.COMPLETED,
            )
            .all()
        )
        overdue = sum(
            1
            for t in open_tasks
            if t.due_date and t.due_date.replace(tzinfo=t.due_date.tzinfo or timezone.utc) < now
        )
        weight = {
            TaskPriority.CRITICAL: 4,
            TaskPriority.HIGH: 3,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 1,
        }
        load_score = sum(weight.get(t.priority, 1) for t in open_tasks) + overdue * 2
        entries.append(
            {
                "user_id": member.id,
                "username": member.username,
                "open_task_count": len(open_tasks),
                "overdue_count": overdue,
                "load_score": float(load_score),
                "recommendation": None,
            }
        )

    if entries:
        entries.sort(key=lambda e: e["load_score"], reverse=True)
        most_loaded = entries[0]
        least_loaded = entries[-1]
        if most_loaded["load_score"] - least_loaded["load_score"] >= 4 and most_loaded["user_id"] != least_loaded["user_id"]:
            most_loaded["recommendation"] = f"Consider reassigning new tasks to {least_loaded['username']} instead"
            least_loaded["recommendation"] = "Has capacity for additional tasks"
        most_loaded_name = most_loaded["username"]
        least_loaded_name = least_loaded["username"]
    else:
        most_loaded_name = None
        least_loaded_name = None

    return {
        "project_id": project_id,
        "entries": entries,
        "most_loaded_user": most_loaded_name,
        "least_loaded_user": least_loaded_name,
    }


def _heuristic_project_insight(db: Session, project) -> dict:
    total = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
    completed = (
        db.query(func.count(Task.id))
        .filter(Task.project_id == project.id, Task.status == TaskStatus.COMPLETED)
        .scalar()
        or 0
    )
    now = datetime.now(timezone.utc)
    overdue = (
        db.query(func.count(Task.id))
        .filter(
            Task.project_id == project.id,
            Task.status != TaskStatus.COMPLETED,
            Task.due_date.isnot(None),
            Task.due_date < now,
        )
        .scalar()
        or 0
    )
    progress = round((completed / total) * 100, 1) if total else 0.0

    highlights = [
        f"{completed} of {total} tasks completed ({progress}% progress)",
    ]
    if overdue:
        highlights.append(f"{overdue} task(s) are currently overdue and need attention")
    else:
        highlights.append("No overdue tasks right now")
    if project.deadline:
        days_to_deadline = (project.deadline - now.date()).days
        if days_to_deadline < 0:
            highlights.append(f"Project deadline passed {abs(days_to_deadline)} day(s) ago")
        else:
            highlights.append(f"{days_to_deadline} day(s) remaining until the project deadline")

    summary = (
        f"'{project.name}' is {progress}% complete with {total - completed} task(s) remaining. "
        + (f"{overdue} task(s) are overdue. " if overdue else "Nothing is overdue. ")
        + "Generated from current task data."
    )
    return {"project_id": project.id, "summary": summary, "highlights": highlights, "generated_by": "heuristic"}


def project_insight(db: Session, project) -> dict:
    heuristic = _heuristic_project_insight(db, project)
    if not settings.ANTHROPIC_API_KEY:
        return heuristic

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        prompt = (
            "Write a two-sentence, plain-language status update for a project manager based on these facts: "
            + "; ".join(heuristic["highlights"])
            + ". Be direct and avoid filler."
        )
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()
        if text:
            heuristic["summary"] = text
            heuristic["generated_by"] = "anthropic"
    except Exception:
        # Any failure (missing package, network, auth, etc.) silently keeps the heuristic summary.
        pass

    return heuristic


def _heuristic_task_summary(task) -> str:
    description = (task.description or "").strip()
    if not description:
        return f"'{task.title}' has no description yet."
    first_sentence = description.split(". ")[0].strip()
    if len(first_sentence) > 220:
        first_sentence = first_sentence[:217] + "..."
    return first_sentence if first_sentence.endswith((".", "!", "?")) else first_sentence + "."


def summarize_task(task) -> dict:
    heuristic_summary = _heuristic_task_summary(task)
    if not settings.ANTHROPIC_API_KEY or not (task.description or "").strip():
        return {"task_id": task.id, "summary": heuristic_summary, "generated_by": "heuristic"}

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=150,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this task in one concise sentence for a teammate:\n\n{task.description}",
                }
            ],
        )
        text = "".join(block.text for block in response.content if getattr(block, "type", "") == "text").strip()
        if text:
            return {"task_id": task.id, "summary": text, "generated_by": "anthropic"}
    except Exception:
        pass

    return {"task_id": task.id, "summary": heuristic_summary, "generated_by": "heuristic"}
