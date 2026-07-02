from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.order import OrderStatus


class OrderBase(BaseModel):
    title: str
    description: str | None = None
    price: Decimal = Decimal("0")
    status: OrderStatus = OrderStatus.NEW


class OrderCreate(OrderBase):
    client_id: int


class OrderUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: Decimal | None = None
    status: OrderStatus | None = None


class OrderRead(OrderBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
