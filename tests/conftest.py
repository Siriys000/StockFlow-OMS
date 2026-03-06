from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.core.db import Base, get_async_session
from src.main import app
from src.modules.auth.models import User, UserRole  # noqa: F401
from src.modules.auth.security import create_access_token, get_password_hash  # noqa: F401

# 1. Движок для создания самой базы данных (подключаемся к дефолтной БД 'postgres')
# Уровень изоляции AUTOCOMMIT обязателен для команды CREATE DATABASE
default_db_url = settings.DATABASE_URL.replace(f"/{settings.POSTGRES_DB}", "/postgres")
sys_engine = create_async_engine(default_db_url, isolation_level="AUTOCOMMIT")

# 2. Движок для наших тестов (смотрит в тестовую БД)
test_engine = create_async_engine(settings.TEST_DATABASE_URL, echo=False)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Подготавливает чистую тестовую БД перед запуском всех тестов.
    """
    # Шаг 1: Проверяем, существует ли тестовая БД. Если нет - создаем.
    async with sys_engine.connect() as conn:
        res = await conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{settings.POSTGRES_TEST_DB}'"))
        if not res.scalar():
            print(f"🛠️ Создаю тестовую БД: {settings.POSTGRES_TEST_DB}...")
            await conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_TEST_DB}"))

    # Шаг 2: Пересоздаем таблицы в тестовой БД (чтобы начать с чистого листа)
    async with test_engine.begin() as conn:
        # Сначала удаляем всё, если что-то осталось от прерванного теста
        await conn.run_sync(Base.metadata.drop_all)
        # Накатываем свежую схему (эквивалент alembic upgrade head для тестов)
        await conn.run_sync(Base.metadata.create_all)

    yield  # 🚀 ЗДЕСЬ ВЫПОЛНЯЮТСЯ ВСЕ ТЕСТЫ СЕССИИ

    # Шаг 3: Очистка после тестов (Drop таблиц)
    # Саму БД оставляем, удаляем только таблицы, чтобы не копить мусор.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await sys_engine.dispose()
    await test_engine.dispose()


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Выдает сессию БД, обернутую в транзакцию (используем test_engine!).
    После завершения теста транзакция откатывается.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session_maker = async_sessionmaker(bind=connection, expire_on_commit=False, class_=AsyncSession)
    session = session_maker()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture()
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    HTTP клиент. Подменяет 'get_async_session' на нашу тестовую сессию с Rollback-ом.
    """

    async def override_get_async_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(db_session: AsyncSession) -> dict[str, str]:
    """Создает тестового админа и возвращает заголовки авторизации."""
    email = "test_admin@example.com"
    password = "password"
    hashed_pwd = get_password_hash(password)

    # Проверяем, нет ли уже такого юзера (на всякий случай)
    # ... (код проверки опустим для краткости, так как db_session чистится) ...

    user = User(email=email, hashed_password=hashed_pwd, role=UserRole.ADMIN, is_active=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Генерируем токен вручную (без обращения к API логина)
    token = create_access_token(data={"sub": str(user.id)})

    return {"Authorization": f"Bearer {token}"}
