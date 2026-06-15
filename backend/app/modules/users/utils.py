"""Вспомогательные функции домена пользователей."""
from datetime import date

from app.db.enums import AgeGroup


def compute_age(birth_date: date, today: date | None = None) -> int:
    today = today or date.today()
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years


def age_group_for(birth_date: date, today: date | None = None) -> AgeGroup:
    """Возрастная группа: 8–10 junior, 11–12 middle, 13–14+ senior."""
    age = compute_age(birth_date, today)
    if age <= 10:
        return AgeGroup.JUNIOR
    if age <= 12:
        return AgeGroup.MIDDLE
    return AgeGroup.SENIOR
