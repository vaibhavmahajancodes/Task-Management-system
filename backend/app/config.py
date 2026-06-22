"""
Centralised application configuration.

All configurable values are read from environment variables (typically
supplied via a `.env` file -- see `.env.example` in the project root).
Nothing here should be hard-coded for a real deployment; change the
environment, not the code.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "Task & Project Management System"
    ENV: str = "development"  # development | production | test
    DEBUG: bool = True
    API_PREFIX: str = "/api"
    FRONTEND_URL: str = "http://localhost:5173"

    # --- Database ---
    # Defaults to a local SQLite file so the API can be explored without
    # standing up Postgres first. Docker Compose overrides this with the
    # real Postgres URL.
    DATABASE_URL: str = "sqlite:///./taskmanager.db"

    # --- Auth / JWT ---
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_use_a_long_random_string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # --- CORS ---
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- Rate limiting ---
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_DEFAULT: str = "200/minute"

    # --- File uploads ---
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_UPLOAD_EXTENSIONS: str = (
        ".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.png,.jpg,.jpeg,.gif,.zip,.ppt,.pptx"
    )

    # --- Background tasks ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # --- Email (optional - falls back to console logging if unset) ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "no-reply@taskmanager.local"
    SMTP_USE_TLS: bool = True

    # --- AI features (optional) ---
    # If unset, the AI service automatically falls back to the built-in
    # rule-based heuristics instead of calling the Anthropic API.
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def allowed_upload_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_UPLOAD_EXTENSIONS.split(",") if ext.strip()]


@lru_cache
def get_settings() -> Settings:
    """Settings are cached so the environment is only parsed once."""
    return Settings()


settings = get_settings()
