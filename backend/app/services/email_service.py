"""
Minimal email sender. If SMTP credentials are not configured (the default
for local development), emails are simply logged to the console instead of
failing the request -- this keeps registration / password reset / deadline
reminder flows fully testable without a real mail server.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

logger = logging.getLogger("taskmanager.email")


def send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.SMTP_HOST:
        logger.info("[DEV EMAIL] To: %s | Subject: %s\n%s", to_email, subject, body)
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject[:255]
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [to_email], msg.as_string())
        return True
    except Exception as exc:
        logger.exception("Failed to send email to %s", to_email)
        return False


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    send_email(
        to_email,
        subject="Reset your Task Manager password",
        body=(
            "We received a request to reset your password.\n\n"
            f"Click the link below to choose a new one (valid for a limited time):\n{reset_link}\n\n"
            "If you did not request this, you can safely ignore this email."
        ),
    )


def send_deadline_reminder_email(to_email: str, task_title: str, due_date: str) -> None:
    send_email(
        to_email,
        subject=f"Reminder: '{task_title}' is due soon",
        body=f"Your task '{task_title}' is due on {due_date}. Log in to Task Manager to review it.",
    )
