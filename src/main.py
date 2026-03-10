from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.logger import setup_logging
from src.modules.auth.router import router as auth_router
from src.modules.inventory.router import router as inventory_router
from src.modules.orders.router import router as orders_router

# Настраиваем логи
setup_logging()
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    log.info("application_startup", message="StockFlow OMS is starting up...")
    yield
    log.info("application_shutdown", message="StockFlow OMS is shutting down...")


app = FastAPI(
    title="StockFlow OMS API",
    description="Система управления заказами и складом",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CorrelationIdMiddleware)

# --- Настройка версионирования ---
# Создаем главный роутер для v1
api_v1_router = APIRouter(prefix="/api/v1")

# Подключаем модули к v1
api_v1_router.include_router(auth_router)
api_v1_router.include_router(inventory_router)
api_v1_router.include_router(orders_router)

# Подключаем v1 к основному приложению
app.include_router(api_v1_router)
# ---------------------------------


@app.get("/health", tags=["System"])
async def healthcheck(session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
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
