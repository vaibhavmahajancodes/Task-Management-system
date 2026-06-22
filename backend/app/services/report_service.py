"""
Builds the data behind the Reports page and renders it as downloadable
CSV, Excel (.xlsx), or PDF files.
"""
import csv
import io
from datetime import datetime, timedelta, timezone
from typing import List

from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.models.user import User


def get_task_completion_trend(db: Session, weeks: int = 8) -> List[dict]:
    """Tasks completed vs. created per week for the last `weeks` weeks."""
    now = datetime.now(timezone.utc)
    results = []
    for i in range(weeks - 1, -1, -1):
        week_start = now - timedelta(days=(i + 1) * 7)
        week_end = now - timedelta(days=i * 7)
        created = (
            db.query(func.count(Task.id)).filter(Task.created_at >= week_start, Task.created_at < week_end).scalar()
            or 0
        )
        completed = (
            db.query(func.count(Task.id))
            .filter(Task.completed_at >= week_start, Task.completed_at < week_end)
            .scalar()
            or 0
        )
        label = week_start.strftime("%b %d")
        results.append({"period": label, "completed": completed, "created": created})
    return results


def get_team_productivity(db: Session) -> List[dict]:
    now = datetime.now(timezone.utc)
    users = db.query(User).filter(User.is_active.is_(True)).all()
    output = []
    for user in users:
        assigned = db.query(func.count(Task.id)).filter(Task.assigned_to == user.id).scalar() or 0
        if assigned == 0:
            continue
        completed = (
            db.query(func.count(Task.id))
            .filter(Task.assigned_to == user.id, Task.status == TaskStatus.COMPLETED)
            .scalar()
            or 0
        )
        overdue = (
            db.query(func.count(Task.id))
            .filter(
                Task.assigned_to == user.id,
                Task.status != TaskStatus.COMPLETED,
                Task.due_date.isnot(None),
                Task.due_date < now,
            )
            .scalar()
            or 0
        )
        output.append(
            {
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "assigned_count": assigned,
                "completed_count": completed,
                "overdue_count": overdue,
                "completion_rate": round((completed / assigned) * 100, 1) if assigned else 0.0,
            }
        )
    return sorted(output, key=lambda r: r["completion_rate"], reverse=True)


def get_project_progress(db: Session) -> List[dict]:
    now_date = datetime.now(timezone.utc).date()
    projects = db.query(Project).filter(Project.is_archived.is_(False)).all()
    output = []
    for project in projects:
        total = db.query(func.count(Task.id)).filter(Task.project_id == project.id).scalar() or 0
        completed = (
            db.query(func.count(Task.id))
            .filter(Task.project_id == project.id, Task.status == TaskStatus.COMPLETED)
            .scalar()
            or 0
        )
        progress = round((completed / total) * 100, 1) if total else 0.0
        is_overdue = bool(project.deadline and project.deadline < now_date and progress < 100)
        output.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "color": project.color,
                "total_tasks": total,
                "completed_tasks": completed,
                "progress_percent": progress,
                "deadline": project.deadline.isoformat() if project.deadline else None,
                "is_overdue": is_overdue,
            }
        )
    return output


def get_deadline_analysis(db: Session) -> List[dict]:
    now = datetime.now(timezone.utc)
    projects = db.query(Project).filter(Project.is_archived.is_(False)).all()
    output = []
    for project in projects:
        tasks = db.query(Task).filter(Task.project_id == project.id).all()
        on_time = sum(
            1
            for t in tasks
            if t.status == TaskStatus.COMPLETED and t.completed_at and t.due_date and t.completed_at <= t.due_date
        )
        overdue = sum(
            1
            for t in tasks
            if t.status != TaskStatus.COMPLETED
            and t.due_date
            and t.due_date.replace(tzinfo=t.due_date.tzinfo or timezone.utc) < now
        )
        upcoming = sum(
            1
            for t in tasks
            if t.status != TaskStatus.COMPLETED
            and t.due_date
            and t.due_date.replace(tzinfo=t.due_date.tzinfo or timezone.utc) >= now
        )
        output.append(
            {
                "project_id": project.id,
                "project_name": project.name,
                "on_time": on_time,
                "overdue": overdue,
                "upcoming": upcoming,
            }
        )
    return output


# --- Exporters -------------------------------------------------------------------------

def export_tasks_csv(tasks: List[Task]) -> io.BytesIO:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["ID", "Title", "Project", "Status", "Priority", "Assignee", "Due Date", "Created At"])
    for t in tasks:
        writer.writerow(
            [
                t.id,
                t.title,
                t.project.name if t.project else "",
                t.status.value,
                t.priority.value,
                t.assignee.username if t.assignee else "Unassigned",
                t.due_date.strftime("%Y-%m-%d") if t.due_date else "",
                t.created_at.strftime("%Y-%m-%d") if t.created_at else "",
            ]
        )
    byte_buffer = io.BytesIO(buffer.getvalue().encode("utf-8"))
    byte_buffer.seek(0)
    return byte_buffer


def export_tasks_excel(tasks: List[Task]) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Tasks"
    headers = ["ID", "Title", "Project", "Status", "Priority", "Assignee", "Due Date", "Created At"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for t in tasks:
        ws.append(
            [
                t.id,
                t.title,
                t.project.name if t.project else "",
                t.status.value,
                t.priority.value,
                t.assignee.username if t.assignee else "Unassigned",
                t.due_date.strftime("%Y-%m-%d") if t.due_date else "",
                t.created_at.strftime("%Y-%m-%d") if t.created_at else "",
            ]
        )

    for column_cells in ws.columns:
        length = max((len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells), default=0)
        ws.column_dimensions[column_cells[0].column_letter].width = min(max(length + 2, 10), 40)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def export_summary_pdf(
    project_progress: List[dict], team_productivity: List[dict], generated_for: str = "Task Manager"
) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f"{generated_for} - Project & Productivity Report", styles["Title"]),
        Paragraph(datetime.now(timezone.utc).strftime("Generated %B %d, %Y"), styles["Normal"]),
        Spacer(1, 0.25 * inch),
        Paragraph("Project Progress", styles["Heading2"]),
    ]

    project_data = [["Project", "Tasks", "Completed", "Progress", "Deadline"]]
    for p in project_progress:
        project_data.append(
            [
                p["project_name"],
                str(p["total_tasks"]),
                str(p["completed_tasks"]),
                f"{p['progress_percent']}%",
                p["deadline"] or "-",
            ]
        )
    project_table = Table(project_data, hAlign="LEFT")
    project_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F6F5E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    elements += [project_table, Spacer(1, 0.3 * inch), Paragraph("Team Productivity", styles["Heading2"])]

    team_data = [["User", "Assigned", "Completed", "Overdue", "Completion Rate"]]
    for u in team_productivity:
        team_data.append(
            [
                u["full_name"] or u["username"],
                str(u["assigned_count"]),
                str(u["completed_count"]),
                str(u["overdue_count"]),
                f"{u['completion_rate']}%",
            ]
        )
    team_table = Table(team_data, hAlign="LEFT")
    team_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F6F5E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]
        )
    )
    elements.append(team_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
