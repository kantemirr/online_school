"""Утилиты кэширования в Redis (JSON-значения с TTL).

Используется каталогом (Этап 3); далее переиспользуется лидербордами и
аналитикой. Значения сериализуются в JSON; инвалидация — по префиксу ключа.
"""
import json
from typing import Any

from app.core.redis import redis_client

DEFAULT_TTL = 300  # 5 минут


async def cache_get_json(key: str) -> Any | None:
    raw = await redis_client.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None


async def cache_set_json(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    await redis_client.set(key, json.dumps(value, ensure_ascii=False, default=str), ex=ttl)


async def invalidate_prefix(prefix: str) -> int:
    """Удаляет все ключи, начинающиеся с prefix. Возвращает число удалённых."""
    removed = 0
    async for key in redis_client.scan_iter(match=f"{prefix}*"):
        await redis_client.delete(key)
        removed += 1
    return removed
