from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # База данных
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # Тестовая БД (с дефолтным значением на случай, если забудем в .env)
    POSTGRES_TEST_DB: str = "pyflow_oms_test"

    # JWT Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Celery & Redis ---
    REDIS_HOST: str = "localhost"  # В докере (prod) будет "redis"
    REDIS_PORT: int = 6379

    # Вычисляемое свойство (не читается из .env напрямую, собирается из частей)
    @property
    def DATABASE_URL(self) -> str:
        # Используем драйвер postgresql+asyncpg для асинхронности
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def TEST_DATABASE_URL(self) -> str:
        # Тот же URL, но с подстановкой тестовой БД
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_TEST_DB}"

    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        # Храним результаты задач тоже в Redis (в 1-й базе)
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Игнорировать лишние переменные в .env
    )


settings = Settings()
