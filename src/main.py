from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.modules.auth.router import router as auth_router
from src.modules.inventory.router import router as inventory_router

app = FastAPI(
    title="StockFlow OMS API",
    description="Система управления заказами и складом",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(inventory_router)


@app.get("/health", tags=["System"])
async def healthcheck(session: AsyncSession = Depends(get_async_session)):
    """
    Проверка работоспособности API и подключения к БД.
    """
    try:
        # Пытаемся выполнить простейший запрос к БД
        await session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        # Если БД упала, мы хотим об этом знать
        return {"status": "error", "database": "disconnected", "details": str(e)}
