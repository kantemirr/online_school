# Деплой CodeKids (Render + Vercel)

Топология: **фронтенд** → Vercel (статика Vite); **бэкенд** (FastAPI web + ARQ worker) → Render;
**Postgres** и **Redis** → Vercel Storage (Vercel Postgres = Neon, Vercel KV = Upstash).
Фронт обращается к бэку через прокси Vercel (`/api/*` → Render), поэтому CORS не нужен.

```
[Браузер] → Vercel (React, /api/* → прокси) → Render (FastAPI web) → Vercel Postgres + Vercel KV
                                                  Render (ARQ worker) ──┘
```

## ⚠️ Ограничения облака
- **Песочница кода** (исполнение в Docker) на Render **недоступна** — нет доступа к Docker-сокету. Приложение **деградирует**: отправка кода → дружелюбное «Автопроверка временно недоступна». Полноценная изоляция демонстрируется **локально** (`docker compose up` + `pytest`).
- **Worker** на Render — отдельный сервис (на бесплатном тарифе background worker может быть платным). Без воркера не отправляются письма и не обрабатываются фоновые задачи — для ревью используйте **демо-аккаунты** (не требуют подтверждения email).
- **SMTP** опционален: для реальной отправки писем задайте `SMTP_*`; иначе регистрация новых пользователей не подтверждается по почте (вход — демо-кредами).

## Шаг 1. Хранилища на Vercel
1. Vercel → **Storage** → создать **Postgres** (Neon). Скопировать `POSTGRES_URL` (вариант **non-pooling**) — это `DATABASE_DSN`.
2. Vercel → **Storage** → создать **KV** (Upstash Redis). Скопировать `REDIS_URL` (формат `rediss://…`) — это `REDIS_DSN`.

## Шаг 2. Бэкенд на Render (Blueprint)
1. Render → **New** → **Blueprint** → выбрать репозиторий (в корне лежит `render.yaml`).
2. Создадутся сервисы `codekids-backend` (web) и `codekids-worker`. Заполнить переменные группы **codekids-shared** и web-сервиса:
   - `DATABASE_DSN` = non-pooling URL из шага 1; `REDIS_DSN` = KV URL; `DB_SSL=true`.
   - `CORS_ORIGINS` = домен фронта (напр. `https://codekids.vercel.app`); `FRONTEND_BASE_URL` — он же.
   - `BOOTSTRAP_ADMIN_PASSWORD` = `admin12345` (или свой); `JWT_SECRET` генерируется автоматически.
   - (опц.) `ANTHROPIC_API_KEY` для ИИ-подсказок.
3. Деплой. `preDeployCommand` (`bash scripts/release.sh`) сам прогонит **миграции + сиды** (создаст таблицы, bootstrap-админа, демо-курс и демо-аккаунты).
4. Проверка: `https://<backend>.onrender.com/api/v1/health` → `{"status":"ok","db":true,"redis":true}`.

## Шаг 3. Фронтенд на Vercel
1. Vercel → **Add New Project** → импортировать репозиторий, **Root Directory = `frontend`**.
2. В `frontend/vercel.json` заменить `REPLACE-WITH-RENDER-BACKEND.onrender.com` на реальный домен бэка с шага 2 (закоммитить).
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
| `DATABASE_DSN` | строка Postgres от провайдера (Vercel/Neon), non-pooling |
| `REDIS_DSN` | строка Redis (`rediss://…`, Vercel KV/Upstash) |
| `DB_SSL` | `true` в облаке (TLS к БД) |
| `JWT_SECRET` | секрет подписи токенов (Render генерирует) |
| `CORS_ORIGINS` | домен(ы) фронта через запятую |
| `FRONTEND_BASE_URL` | базовый URL фронта (ссылки в письмах) |
| `BOOTSTRAP_ADMIN_EMAIL/PASSWORD` | первый администратор |
| `ANTHROPIC_API_KEY` | (опц.) ИИ-подсказки; пусто → эвристика |
| `SMTP_HOST/PORT/EMAIL_FROM` | (опц.) реальная отправка писем |

## Локальный запуск (полный, с песочницей)
```bash
docker compose up -d            # http://localhost:8080
docker compose exec backend pytest -q       # 62 passed
docker compose exec frontend npm test       # Vitest
```
Локально песочница работает полностью (Docker-сокет примонтирован воркеру).
