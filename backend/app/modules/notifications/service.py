"""Логика уведомлений: создание (in-app + email родителю) и чтение."""
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.core.queue import enqueue
from app.db.enums import NotificationType
from app.modules.notifications import repository as repo
from app.modules.notifications.models import Notification
from app.modules.notifications.schemas import NotificationOut


def _out(n: Notification) -> NotificationOut:
    return NotificationOut(
        id=n.id, type=n.type, payload=n.payload_json, is_read=n.is_read, created_at=n.created_at,
    )


# ── Создание уведомлений ─────────────────────────────────────────────────────
async def notify(
    db: AsyncSession, user_id: int, type_: NotificationType, payload: dict,
    *, email_subject: str | None = None, email_html: str | None = None,
) -> None:
    """In-app уведомление пользователю + (опц.) письмо ему самому, если есть email."""
    from app.modules.users.models import User

    db.add(Notification(user_id=user_id, type=type_, payload_json=payload))
    await db.commit()

    if email_subject:
        user = await db.get(User, user_id)
        if user and user.email:
            await enqueue("send_email", to=user.email, subject=email_subject, html=email_html or "")


async def notify_payment(
    db: AsyncSession, parent_user_id: int, *, status: str, amount, receipt_no: str | None,
) -> None:
    await notify(
        db, parent_user_id, NotificationType.PAYMENT_STATUS,
        {"status": status, "amount": str(amount), "receipt_no": receipt_no},
        email_subject="Статус оплаты в CodeKids",
        email_html=(
            f"<p>Статус платежа: <b>{status}</b>, сумма {amount} ₽."
            + (f" Квитанция №{receipt_no}." if receipt_no else "")
            + " Подробности — в личном кабинете.</p>"
        ),
    )


async def notify_student(
    db: AsyncSession, student_id: int, type_: NotificationType, payload: dict,
    *, email_subject: str | None = None, email_html: str | None = None,
) -> None:
    """In-app уведомление ученику + (опц.) письмо родителю в очередь."""
    db.add(Notification(user_id=student_id, type=type_, payload_json=payload))
    await db.commit()

    if email_subject:
        parent_email = await repo.parent_email_of_student(db, student_id)
        if parent_email:
            await enqueue("send_email", to=parent_email, subject=email_subject, html=email_html or "")


# ── Событийные хелперы (вызываются из источников) ────────────────────────────
async def notify_work_checked(db: AsyncSession, student_id: int, submission_id: int, verdict: str | None) -> None:
    await notify_student(
        db, student_id, NotificationType.WORK_CHECKED,
        {"submission_id": submission_id, "verdict": verdict},
        email_subject="Работа вашего ребёнка проверена",
        email_html=(
            "<p>Работа в CodeKids проверена. "
            f"Результат: <b>{verdict or 'оценено'}</b>. Подробности — в личном кабинете.</p>"
        ),
    )


async def notify_new_session(db: AsyncSession, student_id: int, session) -> None:
    await notify_student(
        db, student_id, NotificationType.NEW_SESSION,
        {"session_id": session.id, "starts_at": session.starts_at.isoformat(),
         "meeting_url": session.meeting_url},
        email_subject="Новое занятие в расписании",
        email_html=(
            f"<p>Назначено новое онлайн-занятие на {session.starts_at:%d.%m.%Y %H:%M}. "
            + (f'Ссылка: <a href="{session.meeting_url}">{session.meeting_url}</a></p>'
               if session.meeting_url else "Ссылка появится в расписании.</p>")
        ),
    )


async def notify_achievement(db: AsyncSession, student_id: int, code: str, title: str) -> None:
    await notify_student(
        db, student_id, NotificationType.ACHIEVEMENT,
        {"code": code, "title": title},
        email_subject="Новое достижение!",
        email_html=f"<p>Ваш ребёнок получил достижение «<b>{title}</b>» в CodeKids. Поздравляем!</p>",
    )


async def notify_deadline(db: AsyncSession, student_id: int, assignment_id: int, title: str, due_at) -> None:
    await notify_student(
        db, student_id, NotificationType.DEADLINE,
        {"assignment_id": assignment_id, "title": title, "due_at": due_at.isoformat()},
        email_subject="Приближается срок сдачи задания",
        email_html=(
            f"<p>Скоро срок по заданию «<b>{title}</b>» — до {due_at:%d.%m.%Y %H:%M}. "
            "Загляните в личный кабинет CodeKids.</p>"
        ),
    )


async def notify_due_soon(db: AsyncSession) -> int:
    """Напоминание о заданиях со сроком в ближайшие 24 ч — записанным ученикам,
    ещё не завершившим урок. Вызывается фоновым cron раз в сутки."""
    from datetime import datetime, timedelta, timezone

    from sqlalchemy import select

    from app.db.enums import EnrollmentStatus, LessonProgressStatus
    from app.modules.catalog.models import Assignment, Lesson, Module
    from app.modules.learning.models import Enrollment, LessonProgress

    now = datetime.now(timezone.utc)
    soon = now + timedelta(hours=24)
    due_rows = await db.execute(
        select(Assignment.id, Assignment.title, Assignment.due_at, Assignment.lesson_id, Module.course_id)
        .join(Lesson, Lesson.id == Assignment.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(Assignment.due_at.is_not(None), Assignment.due_at > now, Assignment.due_at <= soon)
    )
    sent = 0
    for aid, title, due_at, lesson_id, course_id in due_rows.all():
        enr_rows = await db.execute(
            select(Enrollment.id, Enrollment.student_id).where(
                Enrollment.course_id == course_id,
                Enrollment.status == EnrollmentStatus.ACTIVE,
            )
        )
        for enr_id, student_id in enr_rows.all():
            status = await db.scalar(
                select(LessonProgress.status).where(
                    LessonProgress.enrollment_id == enr_id,
                    LessonProgress.lesson_id == lesson_id,
                )
            )
            if status == LessonProgressStatus.COMPLETED:
                continue
            await notify_deadline(db, student_id, aid, title, due_at)
            sent += 1
    return sent


# ── Чтение ───────────────────────────────────────────────────────────────────
async def list_mine(db: AsyncSession, user_id: int, *, unread_only: bool, limit: int) -> list[NotificationOut]:
    rows = await repo.list_for_user(db, user_id, unread_only=unread_only, limit=limit)
    return [_out(n) for n in rows]


async def unread_count(db: AsyncSession, user_id: int) -> int:
    return await repo.unread_count(db, user_id)


async def mark_read(db: AsyncSession, user_id: int, notification_id: int) -> None:
    notification = await repo.get_owned(db, user_id, notification_id)
    if notification is None:
        raise NotFoundError("Уведомление не найдено", code="notification_not_found")
    if not notification.is_read:
        notification.is_read = True
        await db.commit()


async def mark_all_read(db: AsyncSession, user_id: int) -> None:
    for notification in await repo.list_for_user(db, user_id, unread_only=True, limit=1000):
        notification.is_read = True
    await db.commit()
