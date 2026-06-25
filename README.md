# CodeKids — веб-приложение онлайн-школы программирования для детей

Платформа дополнительного
ИТ-образования для детей 8–14 лет: самостоятельное прохождение курсов с
сопровождением преподавателей, авто- и ручная проверка заданий, изолированная
автопроверка кода Python, геймификация, контроль успеваемости для родителей.

Запусти Docker Desktop, потом открой C:\Users\qwe\Desktop\online_school> в терминале, в нем напиши docker compose up и по идее все, дальше можно идти по инструкции что ниже идет

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
- Документация API (Swagger): http://localhost:8080/docs — интерактивная схема всех эндпоинтов
- Health-check: http://localhost:8080/api/v1/health → `{"status":"ok","db":true,"redis":true}`
- Письма (MailHog): http://localhost:8025

Сборка образа песочницы (для автопроверки кода):

```bash
docker compose build sandbox
```

## Демо-данные и учётные записи

Заполнить чистую БД реалистичными демо-данными (8 курсов, 30 детей, родители,
преподаватели, группы, платежи) одной командой:

```bash
docker compose exec backend python -m app.db.reset_and_seed
```

| Роль | Логин | Пароль / PIN | Страница входа |
|---|---|---|---|
| Администратор | `admin@codekids.ru` | `admin12345` | `/login` |
| Родитель | `parent@codekids.ru` | `parent12345` | `/login` |
| Преподаватель | `teacher@codekids.ru` | `teacher12345` | `/login` |
| Ученик | `kid` | PIN `1234` | `/login/child` |

Подробное руководство по ролям — [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).

## Запуск без Docker (для разработки)

Нужны Python 3.12, Node 20 и доступные локально PostgreSQL и Redis.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# заполнить DATABASE_URL/REDIS_URL в окружении (см. .env.example)
alembic upgrade head
python -m app.modules.auth.bootstrap        # bootstrap-админ
python -m app.db.reset_and_seed             # демо-данные (dev)
uvicorn app.main:app --reload --port 8000

# Worker (отдельный терминал)
arq app.worker.settings.WorkerSettings

# Frontend (отдельный терминал)
cd frontend && npm install && npm run dev    # http://localhost:5173 (проксирует /api → backend)
```

## Миграции

Текущие миграции Alembic: `initial` → `email nullable` → `last_active_date`
(streak) → `audit_log`. Команды:

```bash
docker compose exec backend alembic upgrade head                      # применить
docker compose exec backend alembic revision --autogenerate -m "..."  # новая
```

## Тесты

```bash
docker compose exec backend pytest -q     # backend (62 теста: unit + интеграция + контрольный пример)
docker compose exec frontend npm test     # frontend (Vitest: утилиты)
```

Матрица тест-кейсов и контрольный пример — [`backend/tests/TESTING.md`](backend/tests/TESTING.md).

## Документация

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — руководство пользователя по ролям (Приложение В).
- [`docs/DIAGRAMS.md`](docs/DIAGRAMS.md) — диаграммы (ER, архитектура, sequence, развёртывание).
- [`DEPLOY.md`](DEPLOY.md) — облачный деплой (Render + Vercel).
- [`backend/tests/TESTING.md`](backend/tests/TESTING.md) — тест-кейсы и контрольный пример.

## Дорожная карта

Реализованы все 14 функциональных этапов (фундамент → модель данных → аутентификация/RBAC →
каталог → прохождение → задания и **песочница** → геймификация → группы/расписание →
уведомления → оплата → аналитика → админ-панель → детский UI → тестирование → облачная
инфраструктура). Осталось по тексту ВКР: Глава 4 (экономика/надёжность).
