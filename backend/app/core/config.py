"""Конфигурация приложения (Pydantic Settings).

Значения читаются из переменных окружения / файла .env. Здесь же
вычисляются строки подключения к PostgreSQL и Redis, чтобы остальной код
не собирал их вручную.
"""
from functools import lru_cache
from typing import Annotated

from pydantic import computed_field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


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
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
