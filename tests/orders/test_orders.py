from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.inventory.models import Product
from src.modules.orders.models import Order


async def test_create_order_success(client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
    """Тест успешного создания заказа и списания товаров."""

    # 1. Подготовка: создаем товар
    product = Product(sku="MACBOOK-PRO", name="MacBook Pro", price=2000.00, quantity=10)
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # 2. Действие: оформляем заказ на 2 штуки
    payload = {"items": [{"product_id": product.id, "quantity": 2}]}

    response = await client.post("/orders/", json=payload, headers=auth_headers)

    # 3. Проверки ответа API
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert float(data["total_amount"]) == 4000.00  # 2000 * 2
    assert len(data["items"]) == 1

    # 4. Проверки БД: Товар списался?
    await db_session.refresh(product)
    assert product.quantity == 8  # 10 - 2

    # Проверки БД: Заказ реально есть в базе?
    stmt = select(Order).where(Order.id == data["id"])
    result = await db_session.execute(stmt)
    order_in_db = result.scalar_one_or_none()
    assert order_in_db is not None


async def test_create_order_insufficient_stock_rollback(
    client: AsyncClient, db_session: AsyncSession, auth_headers: dict
):
    """
    Тест отката транзакции (Rollback):
    Если товара не хватает, заказ НЕ должен создаться.
    """

    # 1. Подготовка: товар в единственном экземпляре
    product = Product(sku="PS5", name="PlayStation 5", price=500.00, quantity=1)
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Запоминаем, сколько заказов было в БД до нашего запроса
    initial_orders_count = len((await db_session.execute(select(Order))).scalars().all())

    # 2. Действие: пытаемся купить 5 штук
    payload = {"items": [{"product_id": product.id, "quantity": 5}]}

    response = await client.post("/orders/", json=payload, headers=auth_headers)

    # 3. Проверки API: должна быть ошибка 400
    assert response.status_code == 400
    assert "Not enough stock" in response.json()["detail"]

    # 4. САМАЯ ВАЖНАЯ ПРОВЕРКА: Транзакция откатилась?

    # Товар остался на месте?
    await db_session.refresh(product)
    assert product.quantity == 1

    # Новый заказ НЕ добавился в базу?
    final_orders_count = len((await db_session.execute(select(Order))).scalars().all())
    assert final_orders_count == initial_orders_count
