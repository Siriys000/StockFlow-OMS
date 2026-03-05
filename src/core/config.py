from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # База данных
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # Вычисляемое свойство (не читается из .env напрямую, собирается из частей)
    @property
    def DATABASE_URL(self) -> str:
        # Используем драйвер postgresql+asyncpg для асинхронности
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Игнорировать лишние переменные в .env
    )


settings = Settings()
