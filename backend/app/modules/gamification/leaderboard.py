"""Лидерборды на Redis sorted sets (глобальный по XP и по курсу по прогрессу)."""
from app.core.redis import redis_client

GLOBAL_KEY = "gam:lb:global"


def course_key(course_id: int) -> str:
    return f"gam:lb:course:{course_id}"


async def update_global(student_id: int, xp: float) -> None:
    await redis_client.zadd(GLOBAL_KEY, {str(student_id): xp})


async def update_course(course_id: int, student_id: int, score: float) -> None:
    await redis_client.zadd(course_key(course_id), {str(student_id): score})


async def top(key: str, n: int = 10) -> list[tuple[str, float]]:
    """Топ-N по убыванию: [(student_id, score), ...]."""
    return await redis_client.zrevrange(key, 0, n - 1, withscores=True)


async def rank(key: str, student_id: int) -> int | None:
    """Ранг ученика (1 — лучший) или None, если не в рейтинге."""
    position = await redis_client.zrevrank(key, str(student_id))
    return (position + 1) if position is not None else None


async def score_of(key: str, student_id: int) -> float | None:
    return await redis_client.zscore(key, str(student_id))


async def clear(key: str) -> None:
    await redis_client.delete(key)
