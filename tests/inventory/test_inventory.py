from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.inventory.models import Product

# Тестовые данные
TEST_SKU = "IPHONE-15-PRO-MAX"
TEST_NAME = "iPhone 15 Pro Max 256GB"
TEST_PRICE = 1499.99
TEST_QUANTITY = 10


# 1. ТЕСТ НА СОЗДАНИЕ ТОВАРА (АДМИН)
async def test_create_product_admin(client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
    """Администратор может создавать товары через API."""

    payload = {"sku": TEST_SKU, "name": TEST_NAME, "price": TEST_PRICE, "quantity": TEST_QUANTITY}

    # Используем фикстуру auth_headers, которая уже содержит токен админа
    response = await client.post("/inventory/", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == TEST_SKU
    assert data["quantity"] == TEST_QUANTITY

    # Проверка в БД через прямую сессию
    stmt = select(Product).where(Product.sku == TEST_SKU)
    result = await db_session.execute(stmt)
    product = result.scalar_one_or_none()

    assert product is not None
    # Приводим к float для сравнения с Decimal из БД
    assert float(product.price) == TEST_PRICE


# 2. ТЕСТ НА СПИСАНИЕ ТОВАРА
async def test_consume_stock_success(client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
    """Пользователь может списать товар, если его достаточно."""

    # Подготовка: создаем товар в БД напрямую
    product = Product(sku="TEST-ITEM-1", name="Test Item", price=100.00, quantity=5)
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Списываем 2 штуки.
    # ВАЖНО: 'amount' передается как Query-параметр (?amount=2)
    consume_amount = 2
    response = await client.post(
        f"/inventory/{product.id}/consume", params={"amount": consume_amount}, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 3  # Остаток: 5 - 2 = 3

    # Финальная проверка в БД
    await db_session.refresh(product)
    assert product.quantity == 3


# 3. ТЕСТ НА ОШИБКУ (НЕДОСТАТОЧНО ТОВАРА)
async def test_consume_stock_insufficient(client: AsyncClient, db_session: AsyncSession, auth_headers: dict):
    """Система должна вернуть 400, если товара на складе меньше, чем запрашивается."""

    # Подготовка: товар с остатком 1
    product = Product(sku="RARE-ITEM", name="Rare Item", price=5000.00, quantity=1)
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Пытаемся списать 2 штуки
    response = await client.post(f"/inventory/{product.id}/consume", params={"amount": 2}, headers=auth_headers)

    assert response.status_code == 400
    assert "Not enough stock" in response.json()["detail"]

    # Проверяем, что в БД ничего не изменилось (атомарность)
    await db_session.refresh(product)
    assert product.quantity == 1
