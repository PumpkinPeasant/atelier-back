from fastapi import APIRouter

from app.api.admin import admin_router
from app.api.public import public_router

api_router = APIRouter()
# Клиентская (публичная) группа: health + витрина каталога.
api_router.include_router(public_router)
# Админская группа: /admin/auth/* и защищённый CRUD.
api_router.include_router(admin_router)
