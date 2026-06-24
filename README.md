<div align="center">

# 🚀 Task & Project Management System

**A production-ready, full-stack platform for modern engineering teams**

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat-square&logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

[✨ Features](#-features) • [🛠️ Tech Stack](#️-tech-stack) • [⚡ Quick Start](#-quick-start) • [🐳 Docker](#-docker-deployment) • [📁 Structure](#-project-structure) • [📖 API Docs](#-api-reference)

</div>

---

## ✨ Features

### 🔐 Authentication & Security
- 🔑 JWT access + refresh token authentication
- 🔒 bcrypt password hashing
- 👥 Role-Based Access Control — **Admin**, **Project Manager**, **Team Member**
- 📧 Password reset via email (console log in dev)
- 🛡️ Rate limiting, CSRF protection, secure file uploads

### 📊 Dashboard
- 📈 Live project progress bars with colour-coded accents
- 🥧 Task breakdown pie chart (completed / pending / overdue)
- 👨‍💻 Team performance bar chart
- 🕐 Real-time activity feed
- 🔢 Stat cards — active projects, completed tasks, overdue items

### 📁 Project Management
- ➕ Create, edit, archive, restore projects
- 🎨 Custom colour accent per project
- 📅 Deadline tracking with overdue indicators
- 🏷️ Status & priority labels (Planning → Active → Completed)
- 👥 Member management with role visibility
- 📊 Per-project progress percentage

### ✅ Task Management
- ➕ Full CRUD with subtasks support
- 🎯 Four priority levels — **Low · Medium · High · Critical**
- 🔄 Four statuses — **To Do · In Progress · Review · Completed**
- 👤 Assignee management
- 📅 Due dates with overdue detection
- 🏷️ Custom labels/tags with hex colours
- 📎 File attachments
- 💬 Threaded comments with @mention support

### 🗂️ Kanban Board
- 🖱️ Drag-and-drop across columns (react-beautiful-dnd)
- ⚡ Live WebSocket updates — other users' moves appear instantly
- ➕ Add tasks directly to any column
- 🎨 Priority-coloured card left borders
- ⚠️ Overdue indicators on cards

### 📅 Calendar View
- 🗓️ Monthly, weekly, and daily views
- 🔵 Task dot indicators on deadline days
- 📋 Sidebar list sorted by due time
- 🔗 Click-through to task detail modal

### 💬 Team Collaboration
- 💬 Task comments with @mention notifications
- 🔔 Real-time in-app notifications (WebSocket push)
- 🟢 Online presence indicators
- 📋 Activity logs across the whole platform

### ⏱️ Time Tracking
- ▶️ Start / stop timer per task
- 🕐 Duration logging with start/end timestamps
- 📊 Timesheet reports aggregated by user
- 📈 Productivity analysis data

### 📈 Reports & Analytics
- 📉 Task completion trend (weekly line chart)
- 👨‍💼 Team productivity table
- ⏰ Deadline analysis stacked bar chart
- 📊 Project progress overview
- 📤 Export to **PDF · Excel · CSV**

### 🤖 AI-Powered Features
> Works offline with built-in heuristics. Upgraded to Claude when `ANTHROPIC_API_KEY` is set.

- 💡 **Priority suggestion** — keyword + deadline analysis
- 📅 **Deadline prediction** — historical task turnaround modelling
- ⚖️ **Workload distribution** — load scoring + rebalance recommendations
- 🔍 **Project insights** — natural-language status summary
- 📝 **Task summarisation** — one-sentence description

### 🌙 UX & Accessibility
- 🌓 Dark / light theme with persistent preference
- 📱 Fully responsive (mobile → desktop)
- ♿ Keyboard navigation, focus-visible outlines, ARIA labels
- 🎨 Space Grotesk + Inter typefaces
- ✨ Subtle animations (reduced-motion safe)

---

## 🛠️ Tech Stack

### 🐍 Backend
| Layer | Technology |
|---|---|
| 🌐 Framework | FastAPI 0.115 |
| 🗃️ ORM | SQLAlchemy 2.0 |
| 🛢️ Database | PostgreSQL 16 (SQLite in dev) |
| 🔄 Migrations | Alembic |
| ✅ Validation | Pydantic v2 |
| 🔐 Auth | python-jose (JWT) + passlib (bcrypt) |
| ⚡ WebSockets | FastAPI native WebSockets |
| 🔁 Background tasks | Celery + Redis |
| 📊 Reports | ReportLab (PDF) + openpyxl (Excel) |
| 🤖 AI | Anthropic Claude API (optional) |
| 🛡️ Rate limiting | slowapi |

### ⚛️ Frontend
| Layer | Technology |
|---|---|
| ⚛️ Framework | React 18.3 + Vite 5 |
| 🧭 Routing | React Router v6 |
| 🎨 Styling | Tailwind CSS v3 |
| 📡 HTTP | Axios (with token-refresh interceptor) |
| 🖱️ Drag & Drop | react-beautiful-dnd |
| 📊 Charts | Recharts |
| 📅 Calendar | react-calendar |
| 🕐 Dates | date-fns |
| 🔔 WebSocket | Native browser WebSocket API |

### 🏗️ Infrastructure
| Layer | Technology |
|---|---|
| 🐳 Containers | Docker + Docker Compose |
| 🔀 Proxy | Nginx 1.27 |
| 🔁 CI/CD | GitHub Actions |
| 💾 Storage | Postgres volume + uploads volume |

---

## ⚡ Quick Start

### Prerequisites
- 🐍 Python 3.11+
- 📦 Node.js 20+

### 1️⃣ Clone & Enter

```bash
git clone <repo-url>
cd task-management-system
```

### 2️⃣ Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env             # edit values as needed

# Initialise database & seed demo data
alembic upgrade head
python app/seed.py

# Start the API server
uvicorn app.main:app --reload
# → http://localhost:8000
# → http://localhost:8000/api/docs  (Swagger UI)
```

### 3️⃣ Frontend Setup

```bash
cd frontend

npm install --legacy-peer-deps
cp .env.example .env

npm run dev
# → http://localhost:5173
```

### 🎭 Demo Accounts

| 👤 Username | 🔑 Password | 🎭 Role |
|---|---|---|
| `admin` | `Admin@12345` | 🛡️ Admin |
| `pmorgan` | `Manager@12345` | 📋 Project Manager |
| `jchen` | `Member@12345` | 👷 Team Member |
| `rkapoor` | `Member@12345` | 👷 Team Member |

---

## 🐳 Docker Deployment

```bash
# 1. Configure environment
cp .env.example .env
# ✏️  Set a strong SECRET_KEY in .env

# 2. Launch everything
docker compose up --build -d

# 3. Open the app
open http://localhost
```

| 🌐 URL | 📄 Description |
|---|---|
| `http://localhost` | ⚛️ React frontend |
| `http://localhost/api/docs` | 📖 Swagger / OpenAPI |
| `http://localhost/api/redoc` | 📘 ReDoc |

> 💡 On first start, the `api` container automatically runs `alembic upgrade head` and `python app/seed.py`.

---

## 📁 Project Structure

```
task-management-system/
│
├── 🐍 backend/
│   ├── alembic/                    # 🗄️  Database migrations
│   │   └── versions/
│   │       └── 0001_initial.py     # Initial schema (all tables)
│   │
│   ├── app/
│   │   ├── 🔐 auth/
│   │   │   ├── jwt_handler.py      # JWT encode / decode
│   │   │   ├── permissions.py      # RBAC dependencies (require_role, get_current_user)
│   │   │   └── security.py         # bcrypt hash / verify + token generation
│   │   │
│   │   ├── 🗃️  database/
│   │   │   └── db.py               # SQLAlchemy engine, SessionLocal, get_db()
│   │   │
│   │   ├── 📦 models/
│   │   │   ├── associations.py     # M2M: project_members, task_tags
│   │   │   ├── attachment.py       # File attachments
│   │   │   ├── audit_log.py        # Audit trail entries
│   │   │   ├── comment.py          # Task comments
│   │   │   ├── notification.py     # In-app notifications
│   │   │   ├── project.py          # Projects + enums
│   │   │   ├── refresh_token.py    # JWT refresh + password reset tokens
│   │   │   ├── tag.py              # Labels / tags
│   │   │   ├── task.py             # Tasks + subtasks + enums
│   │   │   ├── time_log.py         # Time tracking entries
│   │   │   ├── user.py             # Users + roles
│   │   │   └── __init__.py         # Re-exports all models (Alembic autogenerate)
│   │   │
│   │   ├── 🌐 routes/
│   │   │   ├── ai.py               # 🤖 AI endpoints (priority, deadline, workload, insights)
│   │   │   ├── audit.py            # 📋 Audit log (admin only)
│   │   │   ├── auth.py             # 🔐 Register, login, logout, refresh, reset
│   │   │   ├── calendar.py         # 📅 Tasks by date range
│   │   │   ├── comments.py         # 💬 Comment CRUD
│   │   │   ├── dashboard.py        # 📊 Summary, activity, team, progress
│   │   │   ├── files.py            # 📎 Upload, download, delete attachments
│   │   │   ├── notifications.py    # 🔔 Notification management
│   │   │   ├── projects.py         # 📁 Project CRUD + members
│   │   │   ├── reports.py          # 📈 Completion, deadline, exports (PDF/Excel/CSV)
│   │   │   ├── tags.py             # 🏷️  Tag CRUD
│   │   │   ├── tasks.py            # ✅ Task CRUD + Kanban board + subtasks
│   │   │   ├── time_logs.py        # ⏱️  Timer start/stop + timesheet
│   │   │   ├── users.py            # 👥 User management + online presence
│   │   │   └── websocket.py        # ⚡ WS: /ws/notifications + /ws/board/{id}
│   │   │
│   │   ├── ✅ schemas/
│   │   │   ├── ai.py               # AI request / response models
│   │   │   ├── attachment.py       # Attachment response
│   │   │   ├── audit.py            # Audit log response
│   │   │   ├── auth.py             # Login, register, tokens
│   │   │   ├── comment.py          # Comment create / response
│   │   │   ├── common.py           # Page[T], Message
│   │   │   ├── notification.py     # Notification response
│   │   │   ├── project.py          # Project create / update / response
│   │   │   ├── report.py           # Dashboard + report schemas
│   │   │   ├── tag.py              # Tag create / response
│   │   │   ├── task.py             # Task CRUD + Kanban board shapes
│   │   │   ├── time_log.py         # Time log schemas
│   │   │   └── user.py             # User CRUD + summary
│   │   │
│   │   ├── 🔧 services/
│   │   │   ├── ai_service.py       # 🤖 Heuristics + optional Claude API calls
│   │   │   ├── audit_service.py    # log_action() helper
│   │   │   ├── email_service.py    # SMTP sender (console fallback in dev)
│   │   │   ├── file_service.py     # Chunked upload, path traversal defence
│   │   │   ├── notification_service.py  # create_notification(), @mention parser, WS push
│   │   │   ├── report_service.py   # PDF / Excel / CSV export generators
│   │   │   └── websocket_manager.py     # In-memory WS connection registry
│   │   │
│   │   ├── 🛠️  utils/
│   │   │   ├── datetime_utils.py   # utcnow(), ensure_utc(), is_overdue()
│   │   │   └── pagination.py       # paginate(query, page, page_size) → Page dict
│   │   │
│   │   ├── 🧪 tests/
│   │   │   ├── conftest.py         # Fixtures: in-memory DB, TestClient, users, project
│   │   │   ├── test_auth.py        # Register, login, logout, refresh, reset
│   │   │   ├── test_comments.py    # Comment CRUD + ownership checks
│   │   │   ├── test_dashboard_reports.py  # Dashboard + report endpoints
│   │   │   ├── test_projects.py    # Project CRUD + members + archive
│   │   │   ├── test_tasks.py       # Task CRUD + Kanban + subtasks + filters
│   │   │   └── test_time_tracking.py      # Timer start/stop + timesheet
│   │   │
│   │   ├── celery_app.py           # ⚙️  Celery app + beat schedule (daily reminders)
│   │   ├── config.py               # ⚙️  Pydantic-settings (all env vars)
│   │   ├── main.py                 # 🚀 FastAPI app factory, middleware, routers
│   │   ├── rate_limiter.py         # 🛡️  slowapi limiter instance
│   │   ├── seed.py                 # 🌱 Demo data seeder
│   │   └── tasks_celery.py         # 📬 Celery task definitions (deadline reminders)
│   │
│   ├── alembic.ini                 # Alembic config
│   ├── Dockerfile                  # 🐳 Backend container
│   ├── requirements.txt            # 📦 Production dependencies
│   ├── requirements-dev.txt        # 🧪 Dev / CI dependencies (pytest, ruff, mypy)
│   ├── pytest.ini                  # 🧪 Test runner config
│   └── .env.example                # 📋 Environment variable reference
│
├── ⚛️  frontend/
│   ├── src/
│   │   ├── 🧩 components/
│   │   │   ├── common/
│   │   │   │   ├── Modal.jsx       # Portal-based modal dialog
│   │   │   │   └── Primitives.jsx  # Avatar, Badge, Spinner, EmptyState, FullPageSpinner
│   │   │   ├── layout/
│   │   │   │   ├── AppLayout.jsx   # Shell: sidebar + topbar + <Outlet>
│   │   │   │   ├── AuthLayout.jsx  # Split-screen auth pages layout
│   │   │   │   ├── ProtectedRoute.jsx  # Auth guard + optional role check
│   │   │   │   ├── Sidebar.jsx     # Collapsible nav with active-link highlighting
│   │   │   │   └── Topbar.jsx      # Search, notifications bell, theme toggle, user menu
│   │   │   └── tasks/
│   │   │       ├── NewTaskModal.jsx      # Quick task creation modal
│   │   │       └── TaskDetailModal.jsx  # Full task editor (comments, subtasks, timer, AI)
│   │   │
│   │   ├── 🌍 context/
│   │   │   ├── AuthContext.jsx         # login(), logout(), register(), user state
│   │   │   ├── NotificationContext.jsx # WS connection, unread count, markRead()
│   │   │   ├── ThemeContext.jsx        # dark/light theme + localStorage persistence
│   │   │   └── ToastContext.jsx        # showToast(message, type) + toast renderer
│   │   │
│   │   ├── 🪝 hooks/
│   │   │   ├── useBoardSocket.js    # WebSocket subscription for Kanban live updates
│   │   │   ├── useDebounce.js       # Debounced value (search inputs)
│   │   │   └── useLocalStorage.js   # Persistent useState wrapper
│   │   │
│   │   ├── 📄 pages/
│   │   │   ├── AuditLog.jsx         # 📋 Admin audit trail (paginated, filterable)
│   │   │   ├── CalendarView.jsx     # 📅 Month/week/day view with task dots
│   │   │   ├── Dashboard.jsx        # 📊 Stat cards, charts, activity, progress
│   │   │   ├── ForgotPassword.jsx   # 📧 Request reset email
│   │   │   ├── KanbanBoard.jsx      # 🗂️  Drag-and-drop board with live sync
│   │   │   ├── Login.jsx            # 🔐 Login form
│   │   │   ├── NotFound.jsx         # 🚫 404 page
│   │   │   ├── ProjectDetail.jsx    # 📁 Project info, members, AI insights, files
│   │   │   ├── Projects.jsx         # 📁 Project list with progress cards
│   │   │   ├── Register.jsx         # 📝 Registration form
│   │   │   ├── Reports.jsx          # 📈 Charts + PDF/Excel/CSV export
│   │   │   ├── ResetPassword.jsx    # 🔑 Set new password
│   │   │   ├── Settings.jsx         # ⚙️  Profile, password, theme
│   │   │   ├── Tasks.jsx            # ✅ Filterable task table with pagination
│   │   │   └── TeamManagement.jsx   # 👥 Members list, role editor, online indicators
│   │   │
│   │   ├── 🌐 services/
│   │   │   ├── api.js               # Axios instance + JWT injector + refresh interceptor
│   │   │   ├── authService.js       # login, register, logout, me
│   │   │   └── domainServices.js    # All domain API calls (projects, tasks, AI, reports …)
│   │   │
│   │   ├── 🛠️  utils/
│   │   │   └── formatters.js        # timeAgo, shortDate, formatDuration, formatFileSize, humanise
│   │   │
│   │   ├── App.jsx                  # 🧭 Route tree
│   │   ├── main.jsx                 # ⚛️  React root + provider tree
│   │   └── index.css                # 🎨 Tailwind directives + component layer
│   │
│   ├── Dockerfile                   # 🐳 Multi-stage: Vite build → Nginx static
│   ├── index.html                   # 📄 HTML entry point (Google Fonts)
│   ├── package.json                 # 📦 Dependencies
│   ├── tailwind.config.js           # 🎨 Custom design tokens
│   ├── vite.config.js               # ⚡ Vite + API proxy config
│   └── .env.example                 # 📋 VITE_API_URL reference
│
├── 🐳 nginx/
│   └── nginx.conf                   # Reverse proxy (API, WS, SPA, uploads)
│
├── 📖 docs/
│   ├── API.md                       # Full API reference (all 60+ endpoints)
│   └── ARCHITECTURE.md              # System design diagram + data-flow walkthrough
│
├── 🔄 .github/
│   └── workflows/
│       └── ci.yml                   # Lint → Build → Docker build (GitHub Actions)
│
├── 🐳 docker-compose.yml            # 7 services: db, redis, api, worker, beat, frontend, nginx
├── 🛠️  Makefile                     # Dev shortcuts: make dev, make test, make docker-up …
├── 📋 .env.example                  # Root env reference (SECRET_KEY)
├── 🚫 .gitignore                    # Python, Node, .env, uploads, dist
└── 📖 README.md                     # This file
```

---

## 🌐 API Reference

Interactive docs live at **`/api/docs`** (Swagger) once the backend is running.

| 🔑 Module | 📍 Prefix | 📊 Endpoints |
|---|---|---|
| 🔐 Auth | `/api/auth` | register, login, logout, refresh, forgot-password, reset-password |
| 📁 Projects | `/api/projects` | CRUD + archive/restore + members |
| ✅ Tasks | `/api/tasks` | CRUD + Kanban board + subtasks + status update |
| 💬 Comments | `/api/comments` | Edit + delete |
| 🏷️ Tags | `/api/tags` | CRUD |
| 👥 Users | `/api/users` | Profile, password, role management, online |
| 🔔 Notifications | `/api/notifications` | List, mark read, delete |
| 📎 Files | `/api/files` | Upload, download, delete |
| 📊 Dashboard | `/api/dashboard` | Summary, activity, team, progress |
| 📈 Reports | `/api/reports` | Charts data + PDF/Excel/CSV exports |
| 📅 Calendar | `/api/calendar` | Tasks by date range |
| ⏱️ Time Logs | `/api/time-logs` | Timer, timesheet |
| 🤖 AI | `/api/ai` | Priority, deadline, workload, insights, summarise |
| 📋 Audit | `/api/audit` | Full action trail (admin only) |
| ⚡ WebSocket | `/ws/notifications` | Live notifications push |
| ⚡ WebSocket | `/ws/board/{id}` | Live Kanban board sync |

---

## 🧪 Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest app/tests/ -v
```

**Test coverage includes:**
- 🔐 Auth flows (register, login, token refresh, password reset)
- 📁 Project CRUD, archive/restore, member management
- ✅ Task CRUD, Kanban status updates, subtasks, filters
- 💬 Comments with ownership enforcement
- ⏱️ Time tracking (start/stop, active timer detection)
- 📊 Dashboard and report endpoints

---

## ⚙️ Environment Variables

> Full reference: `backend/.env.example`

| 🔧 Variable | 📋 Default | 📖 Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./taskmanager.db` | 🛢️ SQLAlchemy DSN |
| `SECRET_KEY` | *(must change)* | 🔐 JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | ⏱️ Token lifetime |
| `CORS_ORIGINS` | `http://localhost:5173` | 🌐 Allowed origins |
| `REDIS_URL` | `redis://localhost:6379/0` | 🔄 Celery broker |
| `SMTP_HOST` | `""` | 📧 Email relay (blank = console log) |
| `ANTHROPIC_API_KEY` | `""` | 🤖 Enables Claude AI features |
| `MAX_UPLOAD_SIZE_MB` | `25` | 📎 File size limit |
| `UPLOAD_DIR` | `uploads` | 📁 File storage path |

---

## 🚀 Deployment Checklist

- [ ] 🔐 Set a strong `SECRET_KEY` (32+ random bytes)
- [ ] 🛢️ Switch `DATABASE_URL` to managed PostgreSQL
- [ ] 🔄 Point `REDIS_URL` to managed Redis
- [ ] 📧 Configure SMTP credentials for email notifications
- [ ] 🔒 Set `ENV=production` and `DEBUG=false`
- [ ] 🌐 Update `CORS_ORIGINS` and `FRONTEND_URL` to your domain
- [ ] 🤖 Optionally add `ANTHROPIC_API_KEY` for AI features
- [ ] 🐳 Run `docker compose up --build -d`

---

## 🤝 Contributing

1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/amazing-feature`
3. ✅ Run tests: `make test` and `make lint`
4. 💾 Commit: `git commit -m 'feat: add amazing feature'`
5. 🚀 Push & open a Pull Request

---

## 📄 License

MIT © 2026 — Built with ❤️ using FastAPI + React

---

<div align="center">

⭐ **Star this repo if it helped you!** ⭐

</div>
