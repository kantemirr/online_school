"""Клиент очереди ARQ для постановки фоновых задач из API.

Поддерживает единый пул-соединение к Redis (брокеру). Используется, например,
сервисом аутентификации для постановки задачи send_email.
"""
import redis.asyncio as aioredis
from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from app.core.config import get_settings

_settings = get_settings()
_pool: ArqRedis | None = None


def _redis_settings() -> RedisSettings:
    return RedisSettings(
        host=_settings.REDIS_HOST,
        port=_settings.REDIS_PORT,
        database=_settings.REDIS_DB,
    )


async def get_arq_pool() -> ArqRedis:
    global _pool
    if _pool is None:
        _pool = await create_pool(_redis_settings())
    return _pool


async def enqueue(task: str, *args, **kwargs) -> None:
    pool = await get_arq_pool()
    await pool.enqueue_job(task, *args, **kwargs)


# Тип для подсказок
__all__ = ["get_arq_pool", "enqueue", "ArqRedis", "aioredis"]
