from fastapi import APIRouter, Depends, status

from src.modules.auth.dependencies import get_current_active_user
from src.modules.auth.models import User
from src.modules.orders.schemas import OrderCreate, OrderResponse
from src.modules.orders.service import OrderService, get_order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    order_in: OrderCreate,
    # Только авторизованные пользователи могут делать заказы
    current_user: User = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
):
    """Оформить новый заказ (Корзина)."""
    return await service.create_order(user=current_user, order_in=order_in)
