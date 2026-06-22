import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database.db import Base, engine
from app.rate_limiter import limiter
from app.routes import (
    ai,
    audit,
    auth,
    calendar,
    comments,
    dashboard,
    files,
    notifications,
    projects,
    reports,
    tags,
    tasks,
    time_logs,
    users,
    websocket,
)

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger("taskmanager")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "REST + WebSocket API for the Task & Project Management System: "
        "auth & RBAC, projects, tasks, Kanban boards, comments, notifications, "
        "file attachments, time tracking, reporting, and AI-assisted insights."
    ),
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# --- Rate limiting --------------------------------------------------------------------
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again shortly."})


# --- CORS -------------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Startup --------------------------------------------------------------------------
@app.on_event("startup")
def on_startup():
    if settings.DATABASE_URL.startswith("sqlite"):
        # Convenience for local development/demo only. In Postgres/production,
        # schema management is owned entirely by Alembic (`alembic upgrade head`).
        import app.models  # noqa: F401  (ensures all models are registered on Base)

        Base.metadata.create_all(bind=engine)
        logger.info("SQLite schema ensured via create_all() (development mode).")
    logger.info("%s started in %s mode.", settings.APP_NAME, settings.ENV)


# --- Routers ----------------------------------------------------------------------------
api = settings.API_PREFIX
app.include_router(auth.router, prefix=api)
app.include_router(users.router, prefix=api)
app.include_router(projects.router, prefix=api)
app.include_router(tasks.router, prefix=api)
app.include_router(tags.router, prefix=api)
app.include_router(comments.router, prefix=api)
app.include_router(notifications.router, prefix=api)
app.include_router(files.router, prefix=api)
app.include_router(dashboard.router, prefix=api)
app.include_router(reports.router, prefix=api)
app.include_router(calendar.router, prefix=api)
app.include_router(time_logs.router, prefix=api)
app.include_router(ai.router, prefix=api)
app.include_router(audit.router, prefix=api)
app.include_router(websocket.router)  # WebSocket routes are not prefixed with /api


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}


@app.get("/", tags=["Health"])
def root():
    return {
        "message": f"{settings.APP_NAME} API",
        "docs": "/api/docs",
        "health": "/api/health",
    }
