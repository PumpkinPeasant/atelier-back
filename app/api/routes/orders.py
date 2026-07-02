from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep
from app.crud import client as client_crud
from app.crud import order as crud
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderRead])
async def list_orders(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    client_id: int | None = None,
):
    return await crud.list_(session, skip=skip, limit=limit, client_id=client_id)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, session: SessionDep):
    if await client_crud.get(session, payload.client_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")
    return await crud.create(session, payload)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: int, session: SessionDep):
    order = await crud.get(session, order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return order


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(order_id: int, payload: OrderUpdate, session: SessionDep):
    order = await crud.get(session, order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    return await crud.update(session, order, payload)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, session: SessionDep):
    order = await crud.get(session, order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order not found")
    await crud.delete(session, order)
