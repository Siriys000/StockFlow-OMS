.PHONY: up down build test lint format shell logs

# Запуск всей инфраструктуры в фоне
up:
	docker compose up -d

# Остановка контейнеров
down:
	docker compose down

# Пересборка контейнеров (если изменил код)
build:
	docker compose up --build -d

# Запуск тестов локально
test:
	poetry run pytest -v

# Проверка качества кода (Ruff)
lint:
	poetry run ruff check src tests
	poetry run mypy src

# Автоформатирование кода
format:
	poetry run ruff format src tests
	poetry run ruff check --fix src tests

# Посмотреть логи приложения
logs:
	docker compose logs -f app worker
