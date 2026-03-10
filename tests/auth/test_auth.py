from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.models import User, UserRole

# Тестовые данные (константы)
TEST_EMAIL = "test_user@example.com"
TEST_PASSWORD = "strong_password_123"


# 1. ТЕСТ НА РЕГИСТРАЦИЮ
async def test_register_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """Проверяем успешную регистрацию пользователя."""
    payload = {"email": TEST_EMAIL, "password": TEST_PASSWORD}

    response = await client.post("/api/v1/auth/register", json=payload)

    # Проверяем ответ API
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == TEST_EMAIL
    assert "password" not in data  # Пароль не должен возвращаться!
    assert data["role"] == UserRole.CUSTOMER

    # Проверяем, что пользователь реально создался в БД
    stmt = select(User).where(User.email == TEST_EMAIL)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.hashed_password != TEST_PASSWORD  # В БД должен быть хэш, а не чистый пароль!


# 2. ТЕСТ НА ДУБЛИКАТ EMAIL
async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Проверяем, что нельзя создать двух юзеров с одинаковым email."""
    payload = {"email": "duplicate@example.com", "password": "password"}

    # Первый раз - успех
    await client.post("/api/v1/auth/register", json=payload)

    # Второй раз - ошибка 400
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


# 3. ТЕСТ НА ЛОГИН (ПОЛУЧЕНИЕ ТОКЕНА)
async def test_login_user(client: AsyncClient) -> None:
    """Проверяем получение JWT токена."""
    # Сначала регистрируем юзера (используем уникальный email для изоляции)
    email = "login_test@example.com"
    await client.post("/api/v1/auth/register", json={"email": email, "password": TEST_PASSWORD})

    # Пытаемся залогиниться
    # Важно: OAuth2 использует x-www-form-urlencoded, поэтому передаем data=, а не json=
    login_data = {
        "username": email,  # В OAuth2 поле называется username
        "password": TEST_PASSWORD,
    }

    response = await client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # return token_data["access_token"]  # Возвращаем токен для следующего теста


# 4. ТЕСТ НА ДОСТУП К ЗАЩИЩЕННОМУ РОУТУ (/me)
async def test_access_protected_route(client: AsyncClient) -> None:
    """Проверяем доступ к эндпоинту /api/v1/auth/me с токеном."""
    # Получаем токен из предыдущего теста (или логинимся заново)
    # Для чистоты эксперимента лучше залогиниться заново
    email = "me_route@example.com"
    password = "password"
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})

    login_resp = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_resp.json()["access_token"]

    # Делаем запрос с заголовком Authorization
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["email"] == email


# 5. ТЕСТ НА ОТКАЗ В ДОСТУПЕ (RBAC) - Самый интересный!
async def test_admin_route_forbidden_for_customer(client: AsyncClient) -> None:
    """Обычный юзер (Customer) не должен попасть в /admin-only."""
    email = "customer@example.com"
    password = "password"

    # Регистрируем обычного юзера
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})

    # Логинимся
    login_resp = await client.post("/api/v1/auth/login", data={"username": email, "password": password})
    token = login_resp.json()["access_token"]

    # Пытаемся зайти в админку
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/admin-only", headers=headers)

    # Ожидаем 403 Forbidden
    assert response.status_code == 403
    assert response.json()["detail"] == "Operation not permitted"
