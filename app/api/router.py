from fastapi import APIRouter

from app.api.routes import clients, health, materials, orders, products

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(clients.router)
api_router.include_router(orders.router)
api_router.include_router(materials.router)
api_router.include_router(products.router)
