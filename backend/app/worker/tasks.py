"""Фоновые задачи ARQ.

Реализовано:
  ping        — проверка очереди (Этап 0)
  send_email  — отправка письма-уведомления через SMTP (Этап 2/8)

Дальше сюда добавятся:
  code_check, generate_report, evaluate_achievements, recalc_leaderboard.
"""
from app.core.email import send_email_smtp
from app.core.logging import get_logger

logger = get_logger(__name__)


async def ping(ctx: dict) -> str:
    """Тестовая задача: подтверждает, что воркер забирает задания из очереди."""
    logger.info("worker ping")
    return "pong"


async def send_email(ctx: dict, to: str, subject: str, html: str) -> None:
    """Отправляет письмо. Вызывается из API через enqueue_job('send_email', ...)."""
    await send_email_smtp(to=to, subject=subject, html=html)


# Список задач, который видит ARQ WorkerSettings.
FUNCTIONS = [ping, send_email]
