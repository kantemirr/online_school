"""Фоновые задачи ARQ.

На Этапе 0 — только ping для проверки очереди. Дальше сюда добавятся:
  code_check          — проверка кода ученика в песочнице (Этап 5b)
  send_email          — отправка писем-уведомлений (Этап 8)
  generate_report     — формирование отчётов об успеваемости (Этап 10)
  evaluate_achievements — проверка условий достижений (Этап 6)
  recalc_leaderboard  — пересчёт рейтингов (Этап 6)
"""
from app.core.logging import get_logger

logger = get_logger(__name__)


async def ping(ctx: dict) -> str:
    """Тестовая задача: подтверждает, что воркер забирает задания из очереди."""
    logger.info("worker ping")
    return "pong"


# Список задач, который видит ARQ WorkerSettings.
FUNCTIONS = [ping]
