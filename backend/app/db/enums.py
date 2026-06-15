"""Перечислимые типы предметной области.

Хранятся в БД как VARCHAR + CHECK (native_enum=False при объявлении столбцов),
что упрощает миграции и делает ER-схему наглядной. Значения — латиницей,
человекочитаемые подписи формируются на уровне представления.
"""
from enum import StrEnum


class UserRole(StrEnum):
    STUDENT = "student"
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"


class AgeGroup(StrEnum):
    """Возрастная группа ученика (8–14 лет)."""

    JUNIOR = "junior"   # 8–10
    MIDDLE = "middle"   # 11–12
    SENIOR = "senior"   # 13–14


class CourseTrack(StrEnum):
    """Направление обучения."""

    SCRATCH = "scratch"
    PYTHON = "python"
    WEB = "web"
    GAMEDEV = "gamedev"
    ALGORITHMS = "algorithms"


class CourseLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class AssignmentType(StrEnum):
    QUIZ = "quiz"
    CODE = "code"
    PROJECT = "project"


class QuestionKind(StrEnum):
    """Тип вопроса квиза."""

    SINGLE = "single"       # одиночный выбор
    MULTIPLE = "multiple"   # множественный выбор
    MATCHING = "matching"   # сопоставление


class EnrollmentStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LessonProgressStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class SubmissionStatus(StrEnum):
    """Жизненный цикл отправленной работы (общий для квиза/кода/проекта)."""

    QUEUED = "queued"                 # код поставлен в очередь
    RUNNING = "running"               # выполняется в песочнице
    CHECKED = "checked"               # автопроверка завершена
    PENDING_REVIEW = "pending_review"  # проект ждёт преподавателя
    REVIEWED = "reviewed"             # проект проверен
    NEEDS_REVISION = "needs_revision"  # отправлен на доработку


class CodeVerdict(StrEnum):
    """Агрегированный вердикт автопроверки кода."""

    PASSED = "passed"
    FAILED = "failed"
    PARTIAL = "partial"


class AttendanceStatus(StrEnum):
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"


class SubscriptionPlan(StrEnum):
    """Тариф абонемента."""

    COURSE = "course"     # доступ к одному курсу
    MONTHLY = "monthly"   # подписка на месяц
    ANNUAL = "annual"     # подписка на год


class SubscriptionStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class NotificationType(StrEnum):
    WORK_CHECKED = "work_checked"
    NEW_SESSION = "new_session"
    DEADLINE = "deadline"
    ACHIEVEMENT = "achievement"
    PAYMENT_STATUS = "payment_status"
