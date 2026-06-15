#!/usr/bin/env bash
# Релизный шаг для облака (Render preDeployCommand): миграции + сиды.
# Запуск: bash scripts/release.sh   (рабочая директория — /app, контекст backend)
set -e

echo "→ Применяю миграции (alembic upgrade head)"
alembic upgrade head

echo "→ Bootstrap-администратор"
python -m app.modules.auth.bootstrap || true

echo "→ Сиды контента и демо-данных (идемпотентно)"
python -m app.db.seeds_content || true
python -m app.db.seeds_demo || true

echo "✓ Релиз готов"
