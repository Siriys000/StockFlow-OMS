from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings
from src.modules.auth.models import User, UserRole
from src.modules.auth.service import UserService, get_user_service

# Говорим FastAPI (и Swagger-у), где брать токен.
# URL должен точно совпадать с роутом логина!
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Проверяет JWT токен и возвращает пользователя из БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Расшифровываем токен
        # Указываем Mypy, что payload - это словарь
        payload: dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        # Безопасно достаем sub
        user_id_val = payload.get("sub")
        if user_id_val is None:
            raise credentials_exception

        user_id = int(str(user_id_val))

    except (jwt.PyJWTError, ValueError):
        # Ловим ошибки: токен протух, подделан или ID не число
        raise credentials_exception

    # Ищем пользователя в БД (нам нужен новый метод в сервисе, сейчас мы его добавим!)
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверяет, что аккаунт не заблокирован."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Класс-генератор зависимостей для проверки ролей
class RoleChecker:
    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_active_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")
        return user
