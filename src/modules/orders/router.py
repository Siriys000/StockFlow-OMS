from typing import Any

from fastapi import APIRouter, Depends, status

from src.modules.auth.dependencies import get_current_active_user
from src.modules.auth.models import User
from src.modules.orders.schemas import OrderCreate, OrderResponse
from src.modules.orders.service import OrderService, get_order_service
from src.worker.tasks import generate_invoice_pdf, send_order_confirmation

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_new_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    service: OrderService = Depends(get_order_service),
) -> Any:  # Mypy требует возвращаемый тип. FastAPI ожидает объект, который сконвертирует в OrderResponse
    """Оформить новый заказ (Корзина)."""

    # 1. Синхронно создаем заказ в БД (транзакция)
    order = await service.create_order(user=current_user, order_in=order_in)

    # 2. АСИНХРОННО отправляем задачи в очередь Celery (не ждем их выполнения!)
    # метод .delay() кладет задачу в Redis
    send_order_confirmation.delay(
        order_id=order.id,
        user_email=current_user.email,
        # Передаем строку, так как Decimal не дружит с JSON сериализатором по дефолту
        total_amount=str(order.total_amount),
    )

    # Можно запустить несколько задач параллельно
    generate_invoice_pdf.delay(order_id=order.id)

    # 3. Мгновенно возвращаем ответ клиенту (через 5-10мс)
    return order
