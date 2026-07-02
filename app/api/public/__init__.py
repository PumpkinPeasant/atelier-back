from fastapi import APIRouter

from app.api.public import catalog
from app.api.routes import health

public_router = APIRouter()
public_router.include_router(health.router)
public_router.include_router(catalog.router)
