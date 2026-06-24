# Task & Project Management System

A full-stack, production-ready task and project management platform with a **FastAPI** backend and **React** frontend.

## Feature Overview

| Category | Features |
|---|---|
| Auth | JWT login/logout, refresh tokens, password reset, RBAC (Admin / PM / Member) |
| Dashboard | Stats, project progress bars, team performance chart, recent activity feed |
| Projects | CRUD, archive/restore, members, progress tracking, color accents |
| Tasks | CRUD, subtasks, priority/status, due dates, labels/tags, filters, pagination |
| Kanban | Drag-and-drop board, live WebSocket updates from other team members |
| Calendar | Monthly/weekly/daily view with per-day task dots |
| Collaboration | Task comments, @mentions, file attachments, real-time notifications |
| Time Tracking | Start/stop timer per task, timesheet reports |
| Reports | Completion trend, team productivity, deadline analysis, PDF/Excel/CSV export |
| AI (optional) | Priority suggestion, deadline prediction, workload distribution, project insights, task summarisation (heuristic; upgraded with Claude API when `ANTHROPIC_API_KEY` is set) |
| Team | User list, role management, online presence indicator |
| Admin | Audit log with full action history |
| UX | Dark / light theme, responsive layout, toast notifications |

---

## Quick Start (local development, SQLite)

### Prerequisites
- Python 3.11+
- Node.js 20+

### 1. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                # tweak values as needed

# Create all tables in a local SQLite file and seed demo data
alembic upgrade head
python app/seed.py

# Start the API (http://localhost:8000, docs at /docs)
uvicorn app.main:app --reload
```

Demo accounts created by the seed script:

| Username | Password | Role |
|---|---|---|
| `admin` | `Admin@12345` | Admin |
| `pmorgan` | `Manager@12345` | Project Manager |
| `jchen` | `Member@12345` | Team Member |

### 2. Frontend

```bash
cd frontend
npm install --legacy-peer-deps
cp .env.example .env
npm run dev           # Vite dev server → http://localhost:5173
```

The Vite proxy forwards `/api` and `/ws` to `http://localhost:8000` automatically.

---

## Docker Compose (all services in one command)

```bash
cp .env.example .env           # set a strong SECRET_KEY
docker compose up --build -d
```

| URL | Service |
|---|---|
| `http://localhost` | React frontend |
| `http://localhost/api/docs` | Swagger / OpenAPI |
| `http://localhost/api/redoc` | ReDoc |

On first start the `api` container runs `alembic upgrade head` and `python app/seed.py` automatically.

---

## Project Structure

```
task-management-system/
├── backend/
│   ├── alembic/              # Database migrations
│   │   └── versions/
│   ├── app/
│   │   ├── auth/             # JWT, security helpers, RBAC dependencies
│   │   ├── database/         # SQLAlchemy engine + session
│   │   ├── models/           # ORM models (User, Project, Task, …)
│   │   ├── routes/           # FastAPI routers (auth, projects, tasks, …)
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   ├── services/         # Business logic (AI, notifications, files, reports, …)
│   │   ├── celery_app.py     # Celery application + beat schedule
│   │   ├── config.py         # Centralised settings (pydantic-settings)
│   │   ├── main.py           # FastAPI app factory + middleware
│   │   ├── rate_limiter.py   # slowapi rate limiting setup
│   │   └── seed.py           # Demo data seeder
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/       # Primitives, Modal, Spinners
│   │   │   ├── layout/       # Sidebar, Topbar, AppLayout, ProtectedRoute
│   │   │   └── tasks/        # TaskDetailModal, NewTaskModal
│   │   ├── context/          # AuthContext, ThemeContext, NotificationContext, ToastContext
│   │   ├── hooks/            # useBoardSocket
│   │   ├── pages/            # One file per route
│   │   └── services/         # api.js (axios), authService.js, domainServices.js
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
│
├── nginx/
│   └── nginx.conf            # Reverse proxy config
├── .github/workflows/ci.yml  # GitHub Actions – lint + build + docker
├── docker-compose.yml
└── README.md
```

---

## Environment Variables

See `backend/.env.example` for a full list. Key variables:

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./taskmanager.db` | SQLAlchemy DSN |
| `SECRET_KEY` | (must set) | JWT signing key |
| `ANTHROPIC_API_KEY` | `""` | Enables Claude-powered AI features |
| `SMTP_HOST` | `""` | Email relay; if blank, emails log to console |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker / cache |

---

## API Reference

Interactive docs are available at **`/api/docs`** (Swagger) and **`/api/redoc`** (ReDoc) once the backend is running.

---

## Running Background Tasks

```bash
# Worker (processes deadline reminders, etc.)
celery -A app.celery_app worker --loglevel=info

# Scheduler (triggers daily reminder job at 08:00 UTC)
celery -A app.celery_app beat --loglevel=info
```

---

## AI Features

All AI features work **offline** using built-in heuristics (keyword matching, historical task data). To enable Claude-powered narrative summaries and insights, set `ANTHROPIC_API_KEY` in your `.env`. The app falls back to heuristics gracefully if the API is unreachable.

---

## License

MIT
