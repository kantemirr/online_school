"""Ограничение частоты запросов через счётчики Redis (фиксированное окно).

Ключ `auth:rl:{action}:{identifier}` инкрементируется; на первом обращении на
него ставится TTL = окну. Превышение лимита → 429.
"""
import redis.asyncio as aioredis

from app.core.exceptions import AppError


class RateLimitExceeded(AppError):
    status_code = 429
    code = "rate_limited"


async def enforce_rate_limit(
    redis: aioredis.Redis,
    action: str,
    identifier: str,
    *,
    limit: int,
    window_sec: int,
) -> None:
    key = f"auth:rl:{action}:{identifier}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, window_sec)
    if count > limit:
        raise RateLimitExceeded("Слишком много попыток, повторите позже")
