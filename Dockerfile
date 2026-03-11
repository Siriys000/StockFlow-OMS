# Этап 1: Сборка зависимостей
FROM python:3.12-slim as builder

RUN pip install poetry==2.3.2

WORKDIR /app
COPY pyproject.toml poetry.lock ./
# Не создаем виртуальное окружение внутри контейнера
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

# Этап 2: Финальный образ
FROM python:3.12-slim

WORKDIR /app

# Копируем установленные пакеты из builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем исходный код (БЕЗ frontend)
COPY src/ ./src/
COPY migrations/ ./migrations/

# Копируем конфиги
COPY alembic.ini .
COPY pyproject.toml poetry.lock ./

# Открываем порт для FastAPI
EXPOSE 8000

# Команда по умолчанию (будет переопределена в docker-compose)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
