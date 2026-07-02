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

# 4. Запуск dev-сервера
python main.py
# или: uvicorn app.main:app --reload
```

- API: http://localhost:8000/api
- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/api/health

## Миграции

```bash
alembic revision --autogenerate -m "описание"   # создать миграцию по моделям
alembic upgrade head                             # применить
alembic downgrade -1                             # откатить на шаг назад
```
