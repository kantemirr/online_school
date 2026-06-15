"""Unit-тесты логики геймификации (без БД)."""
from datetime import date

from app.modules.gamification.logic import compute_streak, is_earned


def test_streak_same_day_unchanged():
    assert compute_streak(date(2026, 6, 15), date(2026, 6, 15), 3) == 3


def test_streak_yesterday_increments():
    assert compute_streak(date(2026, 6, 14), date(2026, 6, 15), 3) == 4


def test_streak_gap_resets():
    assert compute_streak(date(2026, 6, 10), date(2026, 6, 15), 3) == 1


def test_streak_first_activity():
    assert compute_streak(None, date(2026, 6, 15), 0) == 1


_STATS = {
    "lessons_completed": 2, "courses_completed": 1, "code_passed": 1,
    "xp": 1200, "streak": 7, "has_perfect_module": True,
}


def test_is_earned_each_type():
    assert is_earned({"type": "lessons_completed", "count": 1}, _STATS)
    assert is_earned({"type": "course_completed", "count": 1}, _STATS)
    assert is_earned({"type": "streak_days", "days": 7}, _STATS)
    assert is_earned({"type": "code_passed", "count": 1}, _STATS)
    assert is_earned({"type": "xp_total", "xp": 1000}, _STATS)
    assert is_earned({"type": "module_score_pct", "pct": 100}, _STATS)


def test_is_not_earned_when_below_threshold():
    low = {**_STATS, "xp": 500, "streak": 2, "lessons_completed": 0}
    assert not is_earned({"type": "xp_total", "xp": 1000}, low)
    assert not is_earned({"type": "streak_days", "days": 7}, low)
    assert not is_earned({"type": "lessons_completed", "count": 1}, low)


def test_unknown_condition_false():
    assert not is_earned({"type": "mystery"}, _STATS)
