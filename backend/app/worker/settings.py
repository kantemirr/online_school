"""Конфигурация ARQ-воркера.

Запуск: `arq app.worker.settings.WorkerSettings`
Брокер — тот же Redis, что и кэш приложения (URL из настроек: поддержка rediss:// TLS).
Надёжность: ретраи задач + периодические cron-задачи (истечение абонементов,
пересчёт лидербордов) для согласованности состояния.
"""
from arq import cron
from arq.connections import RedisSettings

from app.core.config import get_settings
from app.worker.tasks import FUNCTIONS, expire_subscriptions, notify_due_soon, recalc_leaderboard

_settings = get_settings()


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(_settings.REDIS_URL)
    functions = FUNCTIONS

    # ── Надёжность ──
    max_tries = 3          # ретраи транзиентных сбоев (например, отправка email)
    job_timeout = 30       # сек на задачу
    keep_result = 3600     # храним результат час
    retry_jobs = True      # переотправлять при сбое воркера

    # ── Периодические задачи ──
    cron_jobs = [
        cron(expire_subscriptions, hour=3, minute=0),  # раз в сутки: истёкшие абонементы → expired
        cron(recalc_leaderboard, minute=0),            # раз в час: пересчёт лидербордов из БД
        cron(notify_due_soon, hour=9, minute=0),       # раз в сутки: напоминания о дедлайнах
    ]
