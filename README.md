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

# 2.1 Инфраструктура для локалки: PostgreSQL + MinIO (бакет создаётся автоматически)
docker compose up -d

# 3. Миграции
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
- `GET /api/catalog/products/by-slug/{slug}` — карточка товара по слагу
- `GET /api/health`
- Автокомплит для селектов (формат `{value, label}`, поиск `?q=`, `?limit=`):
  `GET /api/lookups/categories`, `/api/lookups/types` (fit),
  `/api/lookups/colors`, `/api/lookups/sizes`
- `GET /api/lookups/category-groups` — справочник категорий, сгруппированный
  (группы с вложенными категориями)

**Админские** `/api/admin/*` — требуют авторизации (кроме login/refresh/logout):

- `POST /api/admin/auth/login` — вход, ставит httpOnly-cookie `access_token` (15 мин)
  и `refresh_token` (7 дней)
- `POST /api/admin/auth/refresh` — обновление токенов по refresh-cookie
- `POST /api/admin/auth/logout` — сброс cookie
- `GET  /api/admin/auth/me` — текущий админ
- CRUD: `/api/admin/products`, `/api/admin/materials`,
  `/api/admin/colors`, `/api/admin/sizes`,
  `/api/admin/category-groups`, `/api/admin/categories`,
  `/api/admin/clients`, `/api/admin/orders`
- Фото товара: `POST /api/admin/products/{id}/images` (multipart: `file`,
  опц. `is_main`), `DELETE /api/admin/products/{id}/images/{image_id}`

## Хранение фото (S3 / MinIO)

Файлы фото лежат в S3-совместимом хранилище, в БД — только ключ и публичный URL
(таблица `product_images`, много фото на товар). Локально поднимается **MinIO**
через `docker compose up -d`:

- S3 API: http://localhost:9000, веб-консоль: http://localhost:9001 (minioadmin/minioadmin)
- Бакет `atelier` создаётся автоматически и раздаётся публично на чтение
- Загрузка: только JPEG/PNG/WEBP, до 10 MB; ключ вида `products/{id}/{uuid}.ext`

В проде укажите в `.env` реальный `S3_ENDPOINT_URL`/ключи/бакет и `S3_PUBLIC_URL`
(например, CDN). Ресайз и превью пока не делаются — файл сохраняется как есть.

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
