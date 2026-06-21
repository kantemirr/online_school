# Деплой CodeKids — бесплатно (Render free + Vercel free)

Топология полностью на бесплатных тарифах: **фронтенд + Postgres + Redis** → Vercel
(Marketplace: Neon Postgres + Upstash Redis); **бэкенд** (FastAPI + ARQ-воркер в одном
сервисе) → Render free web. Фронт обращается к бэку через прокси Vercel (`/api/*` →
Render), поэтому CORS не нужен.

```
[Браузер] → Vercel (React SPA, /api/* → прокси) → Render free web
                                                     start.sh: миграции+сиды → arq (фон) + uvicorn
                                                       → Neon Postgres (Vercel Marketplace, free)
                                                       → Upstash Redis  (Vercel Marketplace, free)
```

## ⚠️ Ограничения бесплатного тарифа
- **Сон Render free.** После ~15 мин простоя сервис засыпает; первый запрос «холодный» — грузится ~30–60 с (потом быстро). Воркер спит вместе с сервисом.
- **Песочница кода недоступна.** Render не даёт доступ к Docker-сокету → отправка кода **деградирует**: «Автопроверка временно недоступна» (урок не закрывается). Полная изоляция демонстрируется **локально** (`docker compose up` + `pytest`).
- **Квоты хранилищ.** Neon (Postgres) и Upstash (Redis) на free авто-засыпают/имеют лимиты команд — для демо-нагрузки хватает с запасом (сервис всё равно спит при простое).
- **SMTP опционален.** Без `SMTP_*` письма не отправляются, но **демо-аккаунты уже активны** (создаются сидом) — вход без подтверждения email.

## Шаг 1. Хранилища на Vercel (Marketplace)
1. Vercel → **Storage** → **Create Database** → **Neon (Postgres)** (free). Открыть `.env.local`/Quickstart, скопировать строку подключения варианта **non-pooling** (обычно `DATABASE_URL_UNPOOLED` или `POSTGRES_URL_NON_POOLING`) — это `DATABASE_DSN`.
2. Vercel → **Storage** → **Upstash (Redis)** (free). Скопировать строку `rediss://…` (Redis URL с TLS) — это `REDIS_DSN`.

> Хранилища можно создать и напрямую на neon.tech и upstash.com — результат тот же (нужны строки подключения).

## Шаг 2. Бэкенд на Render (Blueprint, free)
1. Render → **New** → **Blueprint** → выбрать репозиторий (в корне лежит `render.yaml`).
2. Создастся **один** сервис `codekids-backend` (web, `plan: free`). Заполнить переменные группы **codekids-shared** и web-сервиса:
   - `DATABASE_DSN` = non-pooling URL (Neon); `REDIS_DSN` = `rediss://…` (Upstash); `DB_SSL=true`.
   - `CORS_ORIGINS` = домен фронта (напр. `https://codekids.vercel.app`); `FRONTEND_BASE_URL` — он же.
   - `BOOTSTRAP_ADMIN_PASSWORD` = `admin12345` (или свой); `JWT_SECRET` генерируется автоматически.
   - (опц.) `ANTHROPIC_API_KEY` для ИИ-подсказок; (опц.) `SMTP_*` для писем.
3. Деплой. `scripts/start.sh` сам прогонит **миграции + сиды** (таблицы, bootstrap-админ, 8 курсов, демо-аккаунты), затем поднимет **воркер в фоне** и API.
4. Проверка: `https://<backend>.onrender.com/api/v1/health` → `{"status":"ok","db":true,"redis":true}` (первый запрос может «прогреваться»).

## Шаг 3. Фронтенд на Vercel (free)
1. Vercel → **Add New Project** → импортировать репозиторий, **Root Directory = `frontend`**.
2. В `frontend/vercel.json` заменить `REPLACE-WITH-RENDER-BACKEND.onrender.com` на реальный домен бэка из шага 2 (закоммитить).
3. Build настроится автоматически (Vite, `npm run build`, `dist`). Деплой.
4. Открыть домен → лендинг. `/api/*` проксируется на Render (CORS не нужен).

## Шаг 4. Проверка
- Открыть фронт → войти **демо-кредами** (ниже) → пройти по кабинетам.
- Healthcheck бэка зелёный; журнал аудита (`/admin/audit`) пишет действия админа.
- Отправка кода в задании → плашка «недоступно» (ожидаемая деградация в облаке).

## Демо-аккаунты (создаются `seeds_demo`)
| Роль | Где | Логин | Пароль/PIN |
|---|---|---|---|
| Администратор | `/login` | `admin@codekids.ru` | `admin12345` |
| Родитель | `/login` | `parent@codekids.ru` | `parent12345` |
| Преподаватель | `/login` | `teacher@codekids.ru` | `teacher12345` |
| Ребёнок | `/login/child` | `kid` | PIN `1234` |

## Переменные окружения (бэкенд)
| Переменная | Назначение |
|---|---|
| `DATABASE_DSN` | строка Postgres (Neon), **non-pooling** |
| `REDIS_DSN` | строка Redis (`rediss://…`, Upstash) |
| `DB_SSL` | `true` в облаке (TLS к БД) |
| `JWT_SECRET` | секрет подписи токенов (Render генерирует) |
| `CORS_ORIGINS` | домен(ы) фронта через запятую |
| `FRONTEND_BASE_URL` | базовый URL фронта (ссылки в письмах) |
| `BOOTSTRAP_ADMIN_EMAIL/PASSWORD` | первый администратор |
| `ANTHROPIC_API_KEY` | (опц.) ИИ-подсказки; пусто → эвристика |
| `SMTP_HOST/PORT/EMAIL_FROM` | (опц.) реальная отправка писем |

## Если не хватает RAM (free instance — 512 МБ)
Запуск uvicorn + arq в одном контейнере обычно укладывается, но если сервис падает по
памяти — закомментируйте строку `arq … &` в `backend/scripts/start.sh` и передеплойте.
Тогда фоновые задачи не обрабатываются (код-задания висят в «queued»), но регистрация,
обучение, квизы, геймификация и отчёты работают (на синхронных хуках).

## Локальный запуск (полный, с песочницей)
```bash
docker compose up -d            # http://localhost:8080
docker compose exec backend pytest -q       # 62 passed
docker compose exec frontend npm test       # Vitest
```
Локально песочница работает полностью (Docker-сокет примонтирован воркеру).
