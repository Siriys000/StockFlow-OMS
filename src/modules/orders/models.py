import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


# Статусы заказа
class OrderStatus(str, enum.Enum):
    PENDING = "pending"  # Создан, ждет оплаты
    PAID = "paid"  # Оплачен
    SHIPPED = "shipped"  # Отправлен
    DELIVERED = "delivered"  # Доставлен
    CANCELLED = "cancelled"  # Отменен (товары должны вернуться на склад)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Связь с покупателем (кто заказал)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

    # Итоговая сумма заказа (считается при создании)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # ORM связь (позволяет легко получить items при запросе заказа)
    items: Mapped[list["OrderItem"]] = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # К какому заказу относится
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False, index=True)
    # Какой товар куплен
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)

    # Количество купленного товара
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    # Цена ЗА ШТУКУ на момент покупки (важно! цена в каталоге может измениться, а в истории заказа - нет)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # ORM связь обратно к заказу
    order: Mapped["Order"] = relationship("Order", back_populates="items")
