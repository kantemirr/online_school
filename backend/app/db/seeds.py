"""Сиды справочных данных.

Запуск: `python -m app.db.seeds`
Идемпотентно: достижения вставляются/обновляются по уникальному коду.

Справочники направлений, уровней, возрастных групп, типов заданий и статусов
реализованы перечислимыми типами (app/db/enums.py) и отдельных таблиц не
требуют — здесь наполняется единственный справочник-таблица: достижения.
"""
import asyncio

from sqlalchemy import select

from app.db.session import SessionLocal
from app.modules.gamification.models import Achievement

# Базовый набор достижений. condition_json — машиночитаемое условие выдачи,
# которое проверяет фоновая задача evaluate_achievements (Этап 6).
ACHIEVEMENTS: list[dict] = [
    {
        "code": "first_lesson",
        "title": "Первый шаг",
        "description": "Завершён первый урок",
        "icon": "🎯",
        "condition_json": {"type": "lessons_completed", "count": 1},
    },
    {
        "code": "module_perfect",
        "title": "Идеальный модуль",
        "description": "100% по всем заданиям модуля",
        "icon": "💎",
        "condition_json": {"type": "module_score_pct", "pct": 100},
    },
    {
        "code": "course_complete",
        "title": "Курс пройден",
        "description": "Завершён полный курс",
        "icon": "🏆",
        "condition_json": {"type": "course_completed", "count": 1},
    },
    {
        "code": "streak_7",
        "title": "Неделя без пропусков",
        "description": "7 дней активности подряд",
        "icon": "🔥",
        "condition_json": {"type": "streak_days", "days": 7},
    },
    {
        "code": "first_code_passed",
        "title": "Код работает!",
        "description": "Первое код-задание пройдено по всем тестам",
        "icon": "✅",
        "condition_json": {"type": "code_passed", "count": 1},
    },
    {
        "code": "xp_1000",
        "title": "Тысячник",
        "description": "Набрано 1000 очков опыта",
        "icon": "⭐",
        "condition_json": {"type": "xp_total", "xp": 1000},
    },
]


async def seed_achievements() -> int:
    created = 0
    async with SessionLocal() as session:
        for data in ACHIEVEMENTS:
            existing = await session.scalar(
                select(Achievement).where(Achievement.code == data["code"])
            )
            if existing is None:
                session.add(Achievement(**data))
                created += 1
            else:
                existing.title = data["title"]
                existing.description = data["description"]
                existing.icon = data["icon"]
                existing.condition_json = data["condition_json"]
        await session.commit()
    return created


async def main() -> None:
    created = await seed_achievements()
    print(f"seed: achievements upserted, {created} created")


if __name__ == "__main__":
    asyncio.run(main())
