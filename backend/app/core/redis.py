"""Асинхронный клиент Redis (кэш / токены / rate-limit / лидерборды).

Импорт `redis.asyncio` ссылается на установленный пакет redis, а не на этот
модуль (Python использует абсолютные импорты), поэтому коллизии имён нет.
"""
import redis.asyncio as aioredis

from app.core.config import get_settings

_settings = get_settings()

# Пул соединений на всё приложение. decode_responses=True — работаем со строками.
redis_client: aioredis.Redis = aioredis.from_url(
    _settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis() -> aioredis.Redis:
    """FastAPI-зависимость: отдаёт общий клиент Redis."""
    return redis_client
