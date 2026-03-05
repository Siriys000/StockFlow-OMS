from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings

# Создаем асинхронный движок.
# echo=True будет выводить в консоль все SQL-запросы (полезно для отладки, на проде отключаем).
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Фабрика сессий. expire_on_commit=False обязательно для асинхронной алхимии,
# чтобы объекты не "протухали" после коммита транзакции.
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Базовый класс для всех ORM-моделей
class Base(DeclarativeBase):
    pass


# Зависимость (Dependency) для FastAPI.
# Выдает сессию БД на время запроса и корректно ее закрывает.
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
