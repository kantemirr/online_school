"""Реестр ORM-моделей для Alembic.

Импорт всех моделей в один модуль гарантирует, что Base.metadata знает обо
всех таблицах при автогенерации миграций. Порядок импорта не важен —
внешние ключи между модулями SQLAlchemy разрешает по именам таблиц.
"""
from app.db.base import Base

# users
from app.modules.users.models import (  # noqa: F401,E402
    ParentProfile,
    StudentProfile,
    TeacherProfile,
    User,
)

# catalog
from app.modules.catalog.models import (  # noqa: F401,E402
    Assignment,
    CodeTest,
    Course,
    Lesson,
    Module,
    Question,
)

# learning
from app.modules.learning.models import Enrollment, LessonProgress  # noqa: F401,E402

# grading
from app.modules.grading.models import Submission  # noqa: F401,E402

# gamification
from app.modules.gamification.models import (  # noqa: F401,E402
    Achievement,
    StudentAchievement,
)

# scheduling
from app.modules.scheduling.models import (  # noqa: F401,E402
    Attendance,
    Group,
    GroupMember,
    ScheduleSession,
)

# payments
from app.modules.payments.models import Payment, Subscription  # noqa: F401,E402

# notifications
from app.modules.notifications.models import Notification  # noqa: F401,E402

__all__ = ["Base"]
