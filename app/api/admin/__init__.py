from fastapi import APIRouter, Depends

from app.api.admin import auth
from app.api.deps import get_current_admin
from app.api.routes import clients, materials, orders, products

admin_router = APIRouter(prefix="/admin")

# Аутентификация: login/refresh/logout доступны без access-токена
# (защита /auth/me — на уровне самого эндпоинта).
admin_router.include_router(auth.router)

# Остальные админские ресурсы требуют валидный access-токен.
_protected = APIRouter(dependencies=[Depends(get_current_admin)])
_protected.include_router(products.router)
_protected.include_router(materials.router)
_protected.include_router(clients.router)
_protected.include_router(orders.router)
admin_router.include_router(_protected)
