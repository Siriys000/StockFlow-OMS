from typing import Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.modules.auth.models import User
from src.modules.auth.schemas import UserCreate
from src.modules.auth.security import get_password_hash, verify_password


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Проверяет email и пароль. Возвращает User или None, если данные неверны."""
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Ищет пользователя по email."""
        # Используем современный синтаксис SQLAlchemy 2.0 (select)
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        # Возвращает объект User или None
        return result.scalar_one_or_none()

    async def create_user(self, user_in: UserCreate) -> User:
        """Хэширует пароль и сохраняет пользователя в БД."""
        hashed_pwd = get_password_hash(user_in.password)

        new_user = User(email=user_in.email, hashed_password=hashed_pwd)

        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)

        return new_user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Ищет пользователя по ID."""
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


# Провайдер зависимости (Dependency Injection) для FastAPI
def get_user_service(session: AsyncSession = Depends(get_async_session)) -> UserService:
    return UserService(session)
