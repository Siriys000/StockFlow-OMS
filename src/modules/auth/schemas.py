from pydantic import BaseModel, ConfigDict, EmailStr

from src.modules.auth.models import UserRole


# Базовая схема (общие поля)
class UserBase(BaseModel):
    email: EmailStr


# Схема для РЕГИСТРАЦИИ (что мы ожидаем от клиента)
class UserCreate(UserBase):
    password: str


# Схема для ОТВЕТА API (что мы возвращаем клиенту)
# ВАЖНО: Мы никогда не возвращаем пароль (даже хэш)!
class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool

    # Позволяет Pydantic читать данные из ORM-объектов SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# Схема для выдачи JWT токена
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
