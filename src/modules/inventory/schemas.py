from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str
    sku: str
    # Валидация: цена должна быть больше 0, максимум 2 знака после запятой
    price: Decimal = Field(gt=0, decimal_places=2)
    quantity: int = Field(ge=0, default=0)  # ge=0 (не может быть отрицательным)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    # При обновлении все поля опциональны
    name: str | None = None
    price: Decimal | None = Field(None, gt=0, decimal_places=2)
    quantity: int | None = Field(None, ge=0)


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
