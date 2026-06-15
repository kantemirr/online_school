"""Общие зависимости FastAPI.

Здесь собираются переиспользуемые зависимости (БД, Redis, а на Этапе 2 —
текущий пользователь и проверки RBAC), чтобы роутеры импортировали их из
одного места.
"""
from app.core.redis import get_redis  # noqa: F401
from app.db.session import get_db  # noqa: F401

__all__ = ["get_db", "get_redis"]
