from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.config import settings
from src.modules.auth.dependencies import RoleChecker, get_current_active_user
from src.modules.auth.models import User, UserRole
from src.modules.auth.schemas import Token, UserCreate, UserResponse
from src.modules.auth.security import create_access_token
from src.modules.auth.service import UserService, get_user_service

# Префикс /auth будет добавлен ко всем роутам в этом файле
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, user_service: UserService = Depends(get_user_service)) -> Any:
    """
    Регистрация нового пользователя.
    """
    # 1. Делегируем проверку сервису
    existing_user = await user_service.get_user_by_email(user_in.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # 2. Делегируем создание сервису
    new_user = await user_service.create_user(user_in)

    # FastAPI сам преобразует объект SQLAlchemy (new_user)
    # в Pydantic схему (UserResponse) и скроет пароль!
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service)
) -> dict[str, str]:
    """
    Аутентификация пользователя и выдача JWT токена.
    Возвращает словарь, подходящий под схему Token.
    """
    # В form_data.username будет лежать наш email, так как OAuth2 стандарт называет поле username
    user = await user_service.authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Данные, которые зашиваем в токен (обычно это ID пользователя)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Возвращает информацию о текущем авторизованном пользователе.
    (Защищенный роут, требует токен)
    """
    return current_user


@router.get("/admin-only")
async def admin_only_route(current_user: User = Depends(RoleChecker([UserRole.ADMIN]))) -> dict[str, str]:
    """
    Тестовый роут только для администраторов.
    """
    return {"message": f"Welcome, admin {current_user.email}!"}
