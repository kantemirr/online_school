"""Хранилище токенов в Redis: белый список refresh-jti и одноразовые токены.

Refresh-токены действительны, только пока их jti присутствует в Redis. Это
даёт отзыв (logout, смена пароля) и ротацию (на каждом обновлении старый jti
удаляется, новый записывается).

Одноразовые токены (подтверждение email, сброс пароля) — случайные строки,
сопоставленные с user_id и живущие ограниченное время.
"""
import secrets

import redis.asyncio as aioredis

from app.core.config import get_settings

_settings = get_settings()

_REFRESH_TTL = _settings.REFRESH_TOKEN_TTL_DAYS * 24 * 3600
_VERIFY_TTL = 24 * 3600        # подтверждение email — 24 часа
_PWDRESET_TTL = 3600           # сброс пароля — 1 час


def _refresh_key(user_id: int, jti: str) -> str:
    return f"auth:refresh:{user_id}:{jti}"


def _refresh_pattern(user_id: int) -> str:
    return f"auth:refresh:{user_id}:*"


def _ott_key(purpose: str, token: str) -> str:
    return f"auth:{purpose}:{token}"


# ── Refresh-токены ──────────────────────────────────────────────────────────
async def store_refresh(redis: aioredis.Redis, user_id: int, jti: str) -> None:
    await redis.set(_refresh_key(user_id, jti), "1", ex=_REFRESH_TTL)


async def is_refresh_active(redis: aioredis.Redis, user_id: int, jti: str) -> bool:
    return bool(await redis.exists(_refresh_key(user_id, jti)))


async def revoke_refresh(redis: aioredis.Redis, user_id: int, jti: str) -> None:
    await redis.delete(_refresh_key(user_id, jti))


async def revoke_all_refresh(redis: aioredis.Redis, user_id: int) -> int:
    """Удаляет все refresh ученика/пользователя (смена пароля, «выйти везде»)."""
    removed = 0
    async for key in redis.scan_iter(match=_refresh_pattern(user_id)):
        await redis.delete(key)
        removed += 1
    return removed


# ── Одноразовые токены (email-verify / password-reset) ──────────────────────
async def create_one_time(redis: aioredis.Redis, purpose: str, user_id: int) -> str:
    ttl = _VERIFY_TTL if purpose == "verify" else _PWDRESET_TTL
    token = secrets.token_urlsafe(32)
    await redis.set(_ott_key(purpose, token), str(user_id), ex=ttl)
    return token


async def consume_one_time(redis: aioredis.Redis, purpose: str, token: str) -> int | None:
    """Возвращает user_id и сразу удаляет токен (одноразовость). None — если нет."""
    key = _ott_key(purpose, token)
    value = await redis.get(key)
    if value is None:
        return None
    await redis.delete(key)
    return int(value)
