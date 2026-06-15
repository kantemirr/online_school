"""Фоновые задачи ARQ.

Реализовано:
  ping        — проверка очереди (Этап 0)
  send_email  — отправка письма-уведомления через SMTP (Этап 2/8)

Дальше сюда добавятся:
  code_check, generate_report, evaluate_achievements, recalc_leaderboard.
"""
from app.core.email import send_email_smtp
from app.core.logging import get_logger
from app.db import models as _models  # noqa: F401 — регистрирует все таблицы/мапперы (FK-резолв)
from app.modules.grading.code_check import run_code_check

logger = get_logger(__name__)


async def ping(ctx: dict) -> str:
    """Тестовая задача: подтверждает, что воркер забирает задания из очереди."""
    logger.info("worker ping")
    return "pong"


async def send_email(ctx: dict, to: str, subject: str, html: str) -> None:
    """Отправляет письмо. Вызывается из API через enqueue_job('send_email', ...)."""
    await send_email_smtp(to=to, subject=subject, html=html)


async def code_check(ctx: dict, submission_id: int) -> None:
    """Проверка кода ученика в изолированной песочнице по тест-кейсам."""
    await run_code_check(submission_id)


async def evaluate_achievements(ctx: dict, student_id: int) -> int:
    """Фоновая проверка и выдача достижений ученику."""
    from app.db.session import SessionLocal
    from app.modules.gamification import service as gamification

    async with SessionLocal() as db:
        return await gamification.evaluate_achievements(db, student_id)


async def recalc_leaderboard(ctx: dict) -> None:
    """Фоновый пересчёт лидербордов из БД."""
    from app.db.session import SessionLocal
    from app.modules.gamification import service as gamification

    async with SessionLocal() as db:
        await gamification.recalc_leaderboards(db)


async def expire_subscriptions(ctx: dict) -> int:
    """Помечает истёкшие активные абонементы как expired."""
    from app.db.session import SessionLocal
    from app.modules.payments import service as payments

    async with SessionLocal() as db:
        return await payments.expire_subscriptions(db)


async def generate_report(ctx: dict, child_id: int) -> str:
    """Формирует HTML-отчёт об успеваемости ребёнка и сохраняет в uploads."""
    from app.db.session import SessionLocal
    from app.modules.analytics.report import generate_report_file

    async with SessionLocal() as db:
        path = await generate_report_file(db, child_id)
    logger.info("report generated: %s", path)
    return path


async def notify_due_soon(ctx: dict) -> int:
    """Рассылает напоминания о заданиях со сроком в ближайшие 24 ч."""
    from app.db.session import SessionLocal
    from app.modules.notifications import service as notifications

    async with SessionLocal() as db:
        sent = await notifications.notify_due_soon(db)
    logger.info("deadline reminders sent: %s", sent)
    return sent


# Список задач, который видит ARQ WorkerSettings.
FUNCTIONS = [
    ping, send_email, code_check, evaluate_achievements, recalc_leaderboard,
    expire_subscriptions, generate_report, notify_due_soon,
]
