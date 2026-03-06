from decimal import Decimal

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.db import get_async_session
from src.modules.auth.models import User
from src.modules.inventory.service import InventoryService  # Переиспользуем логику склада!
from src.modules.orders.models import Order, OrderItem, OrderStatus
from src.modules.orders.schemas import OrderCreate


class OrderService:
    def __init__(self, session: AsyncSession, inventory_service: InventoryService):
        self.session = session
        self.inventory_service = inventory_service

    async def create_order(self, user: User, order_in: OrderCreate) -> Order:
        """
        Создает заказ и списывает товары в единой транзакции.
        Если товара не хватит - вся транзакция откатится автоматически.
        """
        total_amount = Decimal("0.00")
        order_items = []

        # Начинаем собирать заказ
        for item_in in order_in.items:
            # 1. Безопасно резервируем товар (вызовет SELECT FOR UPDATE внутри InventoryService)
            # Если товара нет - InventoryService выбросит HTTPException(400),
            # и SQLAlchemy автоматически сделает ROLLBACK всей транзакции!
            product = await self.inventory_service.consume_stock(product_id=item_in.product_id, amount=item_in.quantity)

            # 2. Считаем стоимость позиции
            line_total = product.price * item_in.quantity
            total_amount += line_total

            # 3. Готовим позицию заказа (сохраняем историческую цену)
            order_item = OrderItem(product_id=product.id, quantity=item_in.quantity, unit_price=product.price)
            order_items.append(order_item)

        # 4. Создаем сам заказ
        new_order = Order(
            user_id=user.id,
            status=OrderStatus.PENDING,
            total_amount=total_amount,
            items=order_items,  # SQLAlchemy сама свяжет их по Foreign Key!
        )

        self.session.add(new_order)

        # Фиксируем всё в БД
        await self.session.commit()

        # ВАЖНО: После коммита объект new_order "протухает" (expired).
        # Нам нужно загрузить его заново из базы вместе со всеми вложенными items.

        query = (
            select(Order).where(Order.id == new_order.id).options(selectinload(Order.items))  # <--- ЖАДНАЯ ЗАГРУЗКА
        )

        result = await self.session.execute(query)
        return result.scalar_one()  # Возвращаем полностью загруженный заказ


# Dependency Provider (собираем зависимости вместе)
def get_order_service(session: AsyncSession = Depends(get_async_session)) -> OrderService:
    # Передаем ту же самую сессию БД в InventoryService, чтобы они работали в одной транзакции!
    inventory_service = InventoryService(session)
    return OrderService(session, inventory_service)
