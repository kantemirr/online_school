# CodeKids — веб-приложение онлайн-школы программирования для детей

ВКР (РГЭУ РИНХ, 09.03.03 «Прикладная информатика»). Платформа дополнительного
ИТ-образования для детей 8–14 лет: самостоятельное прохождение курсов с
сопровождением преподавателей, авто- и ручная проверка заданий, изолированная
автопроверка кода Python, геймификация, контроль успеваемости для родителей.

## Стек

| Слой | Технологии |
|---|---|
| Backend | FastAPI (async), Pydantic v2, SQLAlchemy 2.0, Alembic |
| СУБД | PostgreSQL 16 |
| Кэш / брокер / токены / лидерборды | Redis 7 |
| Очередь фоновых задач | ARQ (async, поверх Redis) |
| Песочница | Изолированный Docker-контейнер (без сети, лимиты CPU/RAM, cap-drop) |
| Frontend | React 18 + Vite + TypeScript, React Router, Redux Toolkit |
| Инфраструктура | Docker Compose, Nginx reverse-proxy |

## Структура репозитория

```
backend/    FastAPI (модульный монолит: routers → services → repositories → models)
  app/
    core/   конфигурация, логирование, ошибки, клиент Redis
    db/     движок, сессии, базовые модели, реестр моделей для Alembic
    api/    зависимости и роутеры (v1)
    worker/ фоновые задачи ARQ
  alembic/  миграции БД
  tests/    тесты
frontend/   React SPA (Vite dev-server)
sandbox/    образ-исполнитель кода ученика (Этап 5b)
infra/      nginx и прочая инфраструктура
```

## Запуск (Docker)

```bash
cp .env.example .env
docker compose up --build
```

После старта:
- Приложение (через Nginx): http://localhost:8080
- Документация API (Swagger): http://localhost:8080/docs
- Health-check: http://localhost:8080/api/v1/health

Сборка образа песочницы (нужна на Этапе 5b):

```bash
docker compose build sandbox
```

## Миграции

```bash
docker compose exec backend alembic revision --autogenerate -m "описание"
docker compose exec backend alembic upgrade head
```

## Тесты

```bash
docker compose exec backend pytest
```

## Дорожная карта

Полный план реализации по 15 этапам — в файле плана проекта
(`Роадмап реализации`). Текущий статус: **Этап 0 — фундамент**.
