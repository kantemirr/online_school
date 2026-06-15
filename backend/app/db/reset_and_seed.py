"""Сброс dev-БД и чистый посев — ТОЛЬКО для разработки/демо.

Запуск: python -m app.db.reset_and_seed

Дропает и пересоздаёт схему, очищает Redis, ставит alembic stamp head, заводит
bootstrap-админа и заливает справочники + контент (8 курсов) + богатые демо-данные.
НЕ использовать в проде (там схема через миграции в release.sh).
"""
import asyncio
import subprocess

from app.db import models as _models  # noqa: F401 — регистрирует все таблицы в metadata
from app.db.base import Base
from app.db.session import engine


async def _reset_schema_and_redis() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    from app.core.redis import redis_client
    await redis_client.flushdb()


def _run(module: str) -> None:
    subprocess.run(["python", "-m", module], check=True)


def main() -> None:
    print("→ Дроп + пересоздание схемы, очистка Redis")
    asyncio.run(_reset_schema_and_redis())
    print("→ alembic stamp head")
    subprocess.run(["alembic", "stamp", "head"], check=True)
    print("→ bootstrap-администратор")
    _run("app.modules.auth.bootstrap")
    print("→ справочник достижений")
    _run("app.db.seeds")
    print("→ каталог (8 курсов)")
    _run("app.db.seeds_content")
    print("→ демо-данные (родители/дети/группы/платежи)")
    _run("app.db.seeds_demo")
    print("✓ Готово — чистая БД с демо-данными")


if __name__ == "__main__":
    main()
