from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from src.core.config import settings


def get_password_hash(password: str) -> str:
    """Хэширует пароль с помощью bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с хэшем из БД."""
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Генерирует JWT токен."""
    to_encode = data.copy()

    # Устанавливаем время жизни токена
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Подписываем токен нашим секретным ключом
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt
