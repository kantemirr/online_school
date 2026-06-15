# Диаграммы CodeKids

Диаграммы в нотации **Mermaid**. Они рендерятся прямо на GitHub (в этом файле) и
дублируются отдельными файлами в [`docs/diagrams/`](diagrams/) для экспорта.

**Как получить картинку для ВКР (PNG/SVG):**
1. Открыть <https://mermaid.live>, вставить содержимое нужного `.mmd` → «Download PNG/SVG»; или
2. VS Code + расширение *Markdown Preview Mermaid Support* → превью этого файла → скриншот; или
3. CLI: `npx @mermaid-js/mermaid-cli -i docs/diagrams/er.mmd -o er.png`.

| Диаграмма | Файл | Артефакт ВКР |
|---|---|---|
| ER базы данных | [er.mmd](diagrams/er.mmd) | Рис. 4–5 |
| Архитектура (компоненты) | [components.mmd](diagrams/components.mmd) | Рис. 14–15 |
| Sequence: песочница | [seq_sandbox.mmd](diagrams/seq_sandbox.mmd) | Рис. 18 |
| Sequence: оплата | [seq_payment.mmd](diagrams/seq_payment.mmd) | схема оплаты |
| Sequence: JWT | [seq_jwt.mmd](diagrams/seq_jwt.mmd) | Рис. 17 |
| Развёртывание | [deployment.mmd](diagrams/deployment.mmd) | Рис. 16 |

---

## 1. ER-диаграмма базы данных

```mermaid
erDiagram
    USERS ||--o| PARENT_PROFILES : "1:1"
    USERS ||--o| STUDENT_PROFILES : "1:1"
    USERS ||--o| TEACHER_PROFILES : "1:1"
    USERS ||--o{ NOTIFICATIONS : "получает"
    USERS ||--o{ AUDIT_LOG : "actor"

    PARENT_PROFILES ||--o{ STUDENT_PROFILES : "ребёнок"
    PARENT_PROFILES ||--o{ SUBSCRIPTIONS : "оформляет"

    COURSES ||--o{ MODULES : "содержит"
    MODULES ||--o{ LESSONS : "содержит"
    LESSONS ||--o{ ASSIGNMENTS : "содержит"
    ASSIGNMENTS ||--o{ QUESTIONS : "квиз"
    ASSIGNMENTS ||--o{ CODE_TESTS : "тест-кейсы"

    STUDENT_PROFILES ||--o{ ENROLLMENTS : "записан"
    COURSES ||--o{ ENROLLMENTS : "на курс"
    ENROLLMENTS ||--o{ LESSON_PROGRESS : "прогресс"
    LESSONS ||--o{ LESSON_PROGRESS : "по уроку"

    ASSIGNMENTS ||--o{ SUBMISSIONS : "отправки"
    STUDENT_PROFILES ||--o{ SUBMISSIONS : "сдаёт"
    TEACHER_PROFILES ||--o{ SUBMISSIONS : "проверяет"

    ACHIEVEMENTS ||--o{ STUDENT_ACHIEVEMENTS : "выдаётся"
    STUDENT_PROFILES ||--o{ STUDENT_ACHIEVEMENTS : "получает"

    COURSES ||--o{ GROUPS : "по курсу"
    TEACHER_PROFILES ||--o{ GROUPS : "ведёт"
    GROUPS ||--o{ GROUP_MEMBERS : "состав"
    STUDENT_PROFILES ||--o{ GROUP_MEMBERS : "член"
    GROUPS ||--o{ SCHEDULE_SESSIONS : "занятия"
    SCHEDULE_SESSIONS ||--o{ ATTENDANCE : "посещаемость"
    STUDENT_PROFILES ||--o{ ATTENDANCE : "отмечен"

    COURSES ||--o{ SUBSCRIPTIONS : "тариф COURSE"
    SUBSCRIPTIONS ||--o{ PAYMENTS : "оплата"

    USERS {
        bigint id PK
        string email UK
        enum role
        bool is_active
    }
    STUDENT_PROFILES {
        bigint user_id PK,FK
        bigint parent_id FK
        string nickname
        string login_username UK
        int xp
        int streak
    }
    COURSES {
        bigint id PK
        string title
        enum track
        bool is_published
        numeric price
    }
    ASSIGNMENTS {
        bigint id PK
        bigint lesson_id FK
        enum type
        int max_score
    }
    SUBMISSIONS {
        bigint id PK
        bigint assignment_id FK
        bigint student_id FK
        enum status
        enum verdict
        int score
    }
    SUBSCRIPTIONS {
        bigint id PK
        bigint parent_id FK
        enum plan
        enum status
    }
    PAYMENTS {
        bigint id PK
        bigint subscription_id FK
        numeric amount
        enum status
        string receipt_no UK
    }
```

> Полная версия со всеми атрибутами — в [er.mmd](diagrams/er.mmd).

---

## 2. Архитектура (компоненты)

```mermaid
flowchart TB
    subgraph Client["Клиент"]
        Browser["Браузер (4 роли)"]
    end
    Nginx["nginx (статика SPA + /api)"]
    SPA["React 18 + RTK Query + Tailwind"]
    subgraph Back["Backend — FastAPI (модульный монолит)"]
        API["API /api/v1 (routers→services→repositories)"]
        Mods["auth · users · catalog · learning · grading ·<br/>gamification · scheduling · payments ·<br/>notifications · analytics · admin"]
    end
    subgraph Worker["Воркер — ARQ"]
        Tasks["code_check · send_email · evaluate_achievements ·<br/>recalc_leaderboard · expire_subscriptions · generate_report"]
    end
    Runner["Docker-песочница (network none, лимиты,<br/>ro-FS, cap-drop ALL, непривилегированно)"]
    PG[("PostgreSQL")]
    Redis[("Redis: кэш · jti · rate-limit ·<br/>лидерборды · брокер ARQ")]
    SMTP["SMTP / MailHog"]
    Claude["Anthropic API (ИИ-подсказки)"]

    Browser --> Nginx --> SPA
    Nginx --> API --> Mods
    Mods --> PG
    Mods --> Redis
    Redis -- очередь --> Tasks
    Tasks --> PG
    Tasks -- "запуск кода ученика" --> Runner
    Tasks --> SMTP
    Tasks --> Claude
```

---

## 3. Sequence: автопроверка кода в песочнице (защищаемое ядро)

```mermaid
sequenceDiagram
    autonumber
    actor S as Ученик
    participant API as FastAPI (grading)
    participant DB as PostgreSQL
    participant R as Redis (очередь)
    participant W as Воркер ARQ
    participant Box as Docker-песочница
    participant AI as Anthropic API

    S->>API: POST /assignments/{id}/submit/code {code}
    API->>DB: Submission(status=queued)
    API->>R: enqueue code_check
    API-->>S: 202 {submission_id}
    R->>W: code_check(submission_id)
    loop по тест-кейсам
        W->>Box: контейнер (network none, лимиты, timeout)
        Box-->>W: {stdout, stderr, exit_code, timed_out}
    end
    W->>DB: status=checked, verdict, score, result_json
    opt passed
        W->>DB: mark_lesson_completed → XP/достижения
    end
    loop опрос ~1.2с
        S->>API: GET /submissions/{id}
        API-->>S: статус / вердикт / тесты
    end
    opt не passed
        S->>API: GET /submissions/{id}/hint
        API->>AI: код + stderr (без эталонов)
        AI-->>API: подсказка
        API-->>S: {hint, source}
    end
```

---

## 4. Sequence: оплата (имитация шлюза)

```mermaid
sequenceDiagram
    autonumber
    actor P as Родитель
    participant API as FastAPI (payments)
    participant DB as PostgreSQL
    participant SMTP as Email

    P->>API: POST /payments/checkout {plan, course_id?}
    API->>DB: Subscription(pending) + Payment(pending)
    API-->>P: {payment_id, сумма}
    P->>API: POST /payments/{id}/pay {outcome}
    alt paid
        API->>DB: Payment=paid, receipt_no, Subscription=active
        API->>SMTP: письмо родителю
        API-->>P: доступ открыт
        P->>API: GET /payments/{id}/receipt
        API-->>P: квитанция
    else failed
        API->>DB: Payment=failed
        API-->>P: отказ (повтор возможен)
    end
```

---

## 5. Sequence: JWT-аутентификация

```mermaid
sequenceDiagram
    autonumber
    actor U as Пользователь
    participant API as FastAPI (auth)
    participant DB as PostgreSQL
    participant R as Redis (jti)

    U->>API: POST /auth/login
    API->>R: rate-limit (5/60с)
    API->>DB: проверка argon2, is_active
    API->>R: SET auth:refresh:{uid}:{jti} (7д)
    API-->>U: access (15м) + refresh (7д)
    U->>API: POST /auth/refresh {refresh}
    API->>R: проверить jti, удалить старый, записать новый
    API-->>U: новая пара
    U->>API: POST /auth/logout {refresh}
    API->>R: удалить jti
    API-->>U: 204
```

---

## 6. Схема развёртывания

```mermaid
flowchart TB
    subgraph Local["Локально — docker-compose"]
        L_nginx["nginx :8080"] --> L_front["frontend"]
        L_nginx --> L_back["backend"]
        L_back --> L_pg[("postgres")]
        L_back --> L_redis[("redis")]
        L_worker["worker (ARQ)"] --> L_redis
        L_worker --> L_box["sandbox (Docker)"]
        L_worker --> L_mail["mailhog"]
    end
    subgraph Cloud["Облако"]
        C_vercel["Vercel SPA<br/>rewrite /api/* → Render"] -->|/api/*| C_web["Render: web"]
        C_worker["Render: worker"]
        C_web --> C_pg[("Vercel Postgres/Neon")]
        C_web --> C_kv[("Vercel KV/Upstash")]
        C_worker --> C_kv
        C_worker --> C_pg
    end
    Note1["В облаке песочница недоступна (нет Docker-сокета)<br/>→ корректная деградация; полная изоляция — локально."]
    Cloud -.-> Note1
```
