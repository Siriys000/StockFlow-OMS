from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.modules.orders.models import OrderStatus

# --- Схемы для СОЗДАНИЯ заказа ---


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Количество должно быть больше 0")


class OrderCreate(BaseModel):
    # Клиент присылает только список товаров, цену мы посчитаем сами на бэкенде!
    items: list[OrderItemCreate] = Field(min_length=1, description="Заказ не может быть пустым")


# --- Схемы для ОТВЕТА (просмотр заказа) ---


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
    # Включаем список товаров в ответ
    items: list[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
