from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.modules.inventory.models import Product
from src.modules.inventory.schemas import ProductCreate


class InventoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_product(self, product_in: ProductCreate) -> Product:
        """Создание нового товара."""
        new_product = Product(**product_in.model_dump())
        self.session.add(new_product)
        await self.session.commit()
        await self.session.refresh(new_product)
        return new_product

    async def get_all_products(self) -> list[Product]:
        """Получение списка всех товаров."""
        query = select(Product).order_by(Product.id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_product_for_update(self, product_id: int) -> Product:
        """
        Ключевой метод!
        Использует 'with_for_update()', чтобы заблокировать строку в БД
        до конца текущей транзакции. Другие запросы будут ждать.
        """
        query = (
            select(Product)
            .where(Product.id == product_id)
            .with_for_update()  # ПЕССИМИСТИЧЕСКАЯ БЛОКИРОВКА (Race Condition Protection)
        )
        result = await self.session.execute(query)
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    async def consume_stock(self, product_id: int, amount: int) -> Product:
        """
        Безопасное списание товара со склада.
        """
        # 1. Берем товар с блокировкой строки
        product = await self.get_product_for_update(product_id)

        # 2. Проверяем остаток
        if product.quantity < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for product {product.sku}. Available: {product.quantity}",
            )

        # 3. Уменьшаем количество
        product.quantity -= amount

        # 4. Сохраняем (транзакция завершится и блокировка снимется автоматически)
        await self.session.commit()
        await self.session.refresh(product)
        return product


# Dependency Provider
def get_inventory_service(session: AsyncSession = Depends(get_async_session)) -> InventoryService:
    return InventoryService(session)
