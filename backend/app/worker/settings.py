"""Конфигурация ARQ-воркера.

Запуск: `arq app.worker.settings.WorkerSettings`
Брокер — тот же Redis, что и кэш приложения.
"""
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.worker.tasks import FUNCTIONS

_settings = get_settings()


class WorkerSettings:
    redis_settings = RedisSettings(
        host=_settings.REDIS_HOST,
        port=_settings.REDIS_PORT,
        database=_settings.REDIS_DB,
    )
    functions = FUNCTIONS
