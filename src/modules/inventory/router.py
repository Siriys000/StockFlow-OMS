from typing import Any

from fastapi import APIRouter, Depends, status

from src.modules.auth.dependencies import RoleChecker
from src.modules.auth.models import User, UserRole
from src.modules.inventory.schemas import ProductCreate, ProductResponse
from src.modules.inventory.service import InventoryService, get_inventory_service

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    # Только админ может добавлять товары
    current_user: User = Depends(RoleChecker([UserRole.ADMIN])),
    service: InventoryService = Depends(get_inventory_service),
) -> Any:
    """Добавить новый товар на склад (Только для Admin)."""
    _ = current_user  # current_user нам не нужен внутри функции, поэтому используем _
    return await service.create_product(product_in)


@router.get("/", response_model=list[ProductResponse])
async def list_products(service: InventoryService = Depends(get_inventory_service)) -> Any:
    """Получить список всех товаров на складе."""
    return await service.get_all_products()


@router.post("/{product_id}/consume", response_model=ProductResponse)
async def consume_product(
    product_id: int,
    amount: int,
    # Любой активный юзер может "купить" (списать) товар
    service: InventoryService = Depends(get_inventory_service),
) -> Any:
    """Списать товар со склада (имитация покупки)."""
    return await service.consume_stock(product_id, amount)
