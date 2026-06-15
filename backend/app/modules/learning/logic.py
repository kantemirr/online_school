"""Чистая логика прохождения: разблокировка и расчёт прогресса.

Без БД — легко покрывается unit-тестами.
"""


def unlocked_lessons(ordered_ids: list[int], completed: set[int]) -> set[int]:
    """Урок разблокирован, если он первый или предыдущий по порядку завершён."""
    unlocked: set[int] = set()
    prev_completed = True  # первый урок открыт всегда
    for lid in ordered_ids:
        if prev_completed:
            unlocked.add(lid)
        prev_completed = lid in completed
    return unlocked


def progress_pct(total: int, completed_count: int) -> float:
    if total <= 0:
        return 0.0
    return round(completed_count / total * 100, 2)


def first_resume_lesson(
    ordered_ids: list[int], completed: set[int], unlocked: set[int]
) -> int | None:
    """Первый разблокированный незавершённый урок — «продолжить с»."""
    for lid in ordered_ids:
        if lid in unlocked and lid not in completed:
            return lid
    return None
