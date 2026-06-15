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


# Список задач, который видит ARQ WorkerSettings.
FUNCTIONS = [ping, send_email, code_check]
