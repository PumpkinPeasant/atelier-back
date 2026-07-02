# atelier-back

Бэкенд ателье на **FastAPI** + **SQLAlchemy 2.0 (async)** + **PostgreSQL** + **Alembic**.

## Стек

- FastAPI — REST API, авто-документация (Swagger/OpenAPI)
- SQLAlchemy 2.0 (async, asyncpg) — ORM
- Alembic — миграции БД
- Pydantic v2 / pydantic-settings — валидация и конфиг

## Структура

```
app/
  main.py            # сборка FastAPI-приложения
  core/config.py     # настройки из .env
  db/                # Base, mixin'ы, async-сессия
  models/            # ORM-модели (Client, Order)
  schemas/           # Pydantic-схемы запросов/ответов
  crud/              # операции с БД
  api/
    deps.py          # зависимости (сессия)
    router.py        # агрегатор роутеров
    routes/          # health, clients, orders
alembic/             # миграции
main.py              # dev-энтрипоинт (uvicorn --reload)
```

## Запуск

```bash
# 1. Виртуальное окружение и зависимости
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Настройки
cp .env.example .env   # отредактировать доступы к PostgreSQL

# 3. Миграции (нужен запущенный PostgreSQL)
alembic upgrade head

# 4. Администратор для входа в админку
python -m scripts.create_admin admin@atelier.io <password>

# 5. Запуск dev-сервера
python main.py
# или: uvicorn app.main:app --reload
```

- API: http://localhost:8000/api
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## Группы эндпоинтов

**Публичные (витрина)** — без авторизации:

- `GET /api/catalog/products` — каталог товаров (фильтр `?category=`)
- `GET /api/catalog/products/{id}` — карточка товара
- `GET /api/health`

**Админские** `/api/admin/*` — требуют авторизации (кроме login/refresh/logout):

- `POST /api/admin/auth/login` — вход, ставит httpOnly-cookie `access_token` (15 мин)
  и `refresh_token` (7 дней)
- `POST /api/admin/auth/refresh` — обновление токенов по refresh-cookie
- `POST /api/admin/auth/logout` — сброс cookie
- `GET  /api/admin/auth/me` — текущий админ
- CRUD: `/api/admin/products`, `/api/admin/materials`,
  `/api/admin/clients`, `/api/admin/orders`

## Авторизация

JWT access + refresh токены передаются в **httpOnly-cookie** (недоступны из JS,
защита от XSS). Access живёт 15 мин, refresh — 7 дней (настраивается в `.env`).
Access-токен проверяется зависимостью `get_current_admin` для всех защищённых
эндпоинтов. В проде обязательно задать `SECRET_KEY` и `COOKIE_SECURE=true` (HTTPS).

## Миграции

```bash
alembic revision --autogenerate -m "описание"   # создать миграцию по моделям
alembic upgrade head                             # применить
alembic downgrade -1                             # откатить на шаг назад
```
