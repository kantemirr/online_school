#!/usr/bin/env bash
# Старт для бесплатного Render web-сервиса: миграции+сиды, затем воркер и API
# в одном контейнере (отдельный платный worker-сервис не нужен).
# Рабочая директория — /app (контекст backend). startCommand: bash scripts/start.sh
set -e

# Миграции + bootstrap-админ + сиды (идемпотентно)
bash scripts/release.sh

# ARQ-воркер в фоне того же контейнера (best-effort: если упадёт — web живёт).
# Если бесплатному инстансу (512 МБ) не хватит RAM — закомментируйте строку ниже
# (код-задания будут висеть в «queued», остальное работает на синхронных хуках).
arq app.worker.settings.WorkerSettings &

# API на переднем плане (главный процесс сервиса)
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
