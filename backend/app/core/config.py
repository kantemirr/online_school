"""Конфигурация приложения (Pydantic Settings).

Значения читаются из переменных окружения / файла .env. Здесь же
вычисляются строки подключения к PostgreSQL и Redis, чтобы остальной код
не собирал их вручную.
"""
from functools import lru_cache
from typing import Annotated

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


def _normalize_pg_dsn(dsn: str) -> str:
    """Приводит DSN провайдера (Vercel Postgres/Neon) к asyncpg-формату.

    Убирает query-параметры libpq (sslmode/channel_binding) — asyncpg их не
    понимает (TLS включается отдельно через DB_SSL), и нормализует схему.
    """
    base = dsn.split("?", 1)[0]
    for prefix in ("postgresql+asyncpg://", "postgresql://", "postgres://"):
        if base.startswith(prefix):
            return "postgresql+asyncpg://" + base[len(prefix):]
    return base


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Общее ──
    PROJECT_NAME: str = "CodeKids — онлайн-школа программирования"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ── PostgreSQL ──
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "app"
    POSTGRES_PASSWORD: str = "app"
    POSTGRES_DB: str = "codekids"

    # ── Redis ──
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # ── Облако: полные строки подключения от провайдера (Vercel Postgres/KV) ──
    # Заданы → используются вместо частей выше. REDIS_DSN может быть rediss:// (TLS).
    DATABASE_DSN: str | None = None
    REDIS_DSN: str | None = None
    DB_SSL: bool = False  # TLS к БД (включить в облаке: Neon/Vercel Postgres)

    # ── JWT (используется на Этапе 2) ──
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_TTL_MIN: int = 15
    REFRESH_TOKEN_TTL_DAYS: int = 7

    # ── Загрузка проектов (Этап 5c) ──
    UPLOADS_DIR: str = "/data/uploads"

    # ── Песочница (Этап 5b) ──
    SANDBOX_IMAGE: str = "codekids-sandbox:latest"
    SANDBOX_MEM_LIMIT: str = "128m"
    SANDBOX_CPU_LIMIT: float = 0.5
    SANDBOX_PIDS_LIMIT: int = 64
    SANDBOX_TIMEOUT_SEC: int = 8

    # ── Email (SMTP → MailHog в dev) ──
    SMTP_HOST: str = "mailhog"
    SMTP_PORT: int = 1025
    EMAIL_FROM: str = "no-reply@codekids.local"
    FRONTEND_BASE_URL: str = "http://localhost:8080"

    # ── ИИ-подсказки (Anthropic) ──
    ANTHROPIC_API_KEY: str = ""  # пусто → фолбэк на эвристику
    AI_HINT_MODEL: str = "claude-haiku-4-5"
    AI_HINT_RATE_LIMIT: int = 10  # подсказок в час на ученика

    # ── Bootstrap-администратор ──
    # Домен не .local/.example/.test — их отвергает email-валидатор (EmailStr).
    BOOTSTRAP_ADMIN_EMAIL: str = "admin@codekids.ru"
    BOOTSTRAP_ADMIN_PASSWORD: str = "admin12345"

    # ── CORS ──
    # NoDecode отключает JSON-парсинг env-значения; строку "a,b,c" разбирает валидатор ниже.
    CORS_ORIGINS: Annotated[list[str], NoDecode] = [
        "http://localhost:8080",
        "http://localhost:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_DSN:
            return _normalize_pg_dsn(self.DATABASE_DSN)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_DSN:
            return self.REDIS_DSN
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
