"""Unit-тесты чистой логики прохождения (без БД)."""
from app.modules.learning.logic import (
    first_resume_lesson,
    progress_pct,
    unlocked_lessons,
)


def test_unlocked_sequential():
    ids = [1, 2, 3, 4]
    assert unlocked_lessons(ids, set()) == {1}
    assert unlocked_lessons(ids, {1}) == {1, 2}
    assert unlocked_lessons(ids, {1, 2}) == {1, 2, 3}
    assert unlocked_lessons(ids, {1, 2, 3, 4}) == {1, 2, 3, 4}


def test_progress_pct():
    assert progress_pct(4, 1) == 25.0
    assert progress_pct(4, 4) == 100.0
    assert progress_pct(0, 0) == 0.0
    assert progress_pct(3, 1) == 33.33


def test_resume_lesson():
    ids = [1, 2, 3]
    assert first_resume_lesson(ids, set(), {1}) == 1
    assert first_resume_lesson(ids, {1}, {1, 2}) == 2
    assert first_resume_lesson(ids, {1, 2, 3}, {1, 2, 3}) is None
