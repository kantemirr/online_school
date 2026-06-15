"""Тесты модели данных (Этап 1): полнота схемы и корректность мапперов."""
from sqlalchemy.orm import configure_mappers

import app.db.models as models

EXPECTED_TABLES = {
    "users", "parent_profiles", "student_profiles", "teacher_profiles",
    "courses", "modules", "lessons", "assignments", "questions", "code_tests",
    "enrollments", "lesson_progress", "submissions",
    "achievements", "student_achievements",
    "groups", "group_members", "schedule_sessions", "attendance",
    "subscriptions", "payments", "notifications",
}


def test_all_entities_present():
    tables = set(models.Base.metadata.tables.keys())
    assert EXPECTED_TABLES <= tables
    assert len(EXPECTED_TABLES) == 22


def test_mappers_configure():
    # Падает при ошибках в relationship/ForeignKey между модулями.
    configure_mappers()
