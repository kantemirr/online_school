"""Чистая логика геймификации (без БД): streak и условия достижений."""
from datetime import date, timedelta
from typing import Any


def compute_streak(last_active: date | None, today: date, streak: int) -> int:
    """Серия активных дней.

    Сегодня уже отмечались → без изменений; вчера → +1; иначе (разрыв или
    первая активность) → сброс в 1.
    """
    if last_active == today:
        return streak
    if last_active == today - timedelta(days=1):
        return streak + 1
    return 1


def is_earned(condition: dict, stats: dict[str, Any]) -> bool:
    """Выполнено ли условие достижения для агрегированной статистики ученика."""
    kind = (condition or {}).get("type")
    if kind == "lessons_completed":
        return stats["lessons_completed"] >= condition.get("count", 1)
    if kind == "course_completed":
        return stats["courses_completed"] >= condition.get("count", 1)
    if kind == "streak_days":
        return stats["streak"] >= condition.get("days", 7)
    if kind == "code_passed":
        return stats["code_passed"] >= condition.get("count", 1)
    if kind == "xp_total":
        return stats["xp"] >= condition.get("xp", 1000)
    if kind == "module_score_pct":
        return stats.get("has_perfect_module", False)
    return False
