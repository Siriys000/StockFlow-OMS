# StockFlow OMS
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://Siriys000.github.io/StockFlow-OMS/)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![alt text](https://img.shields.io/badge/Redis-7.0-red.svg)
![alt text](https://img.shields.io/badge/Celery-5.3-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![alt text](https://github.com/Siriys000/StockFlow-OMS/actions/workflows/ci.yml/badge.svg)

**StockFlow OMS** — это проект системы управления заказами, разработанный для демонстрации бэкенд-разработки на Python.

### 🎯 Цель проекта
Цель репозитория — применение промышленного стека технологий и архитектурных паттернов в бизнес-задаче.

### 🛡 Что здесь реализовано (Production Standards):
- **Type Safety:** Строгая типизация с Mypy (strict mode).
- **Architecture:** Модульный монолит с разделением ответственности.
- **Reliability:** Работа с конкурентностью в БД.
- **Security:** JWT-авторизация и Role-Based Access Control (**RBAC**) — разграничение прав для Admin и Customer.
- **Distributed Tasks**: Фоновая обработка тяжелых задач через Celery + Redis.
- **Testing:** Изолированные тесты с транзакционным роллбэком (Pytest + AsyncIO).
- **CI/CD:** Автоматизация проверок и контейнеризация.
- **Observability:** Структурное логирование и готовность к мониторингу.

### ⚠️ Ограничения (Disclaimer)
Проект является учебным полигоном (Sandbox). В нем упрощены некоторые аспекты.

## 🛠 Технологический стек

- **Core:** Python 3.12, FastAPI, Pydantic V2
- **Database:** PostgreSQL 15, SQLAlchemy 2.0 (Async), Alembic
- **Async Tasks:** Celery, Redis
- **Frontend (UI Extension):** React, Vite, Tailwind CSS, Axios
- **Deployment:** Docker, Docker Compose, Makefile, GitHub Actions (CI)
- **Quality:** Pytest, Ruff, Mypy

## 🏗 Архитектура

Подробное описание архитектуры см. в [docs/architecture.md](docs/architecture.md).

## 📖 Документация
Подробное описание API доступно на: 

👉 **[Siriys000.github.io/StockFlow-OMS/](https://Siriys000.github.io/StockFlow-OMS/)**

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.12+
- Docker & Docker Compose
- Poetry

### Установка и запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Siriys000/StockFlow-OMS.git
   cd StockFlow-OMS
   ```

2. **Настройте переменные окружения:**
   ```bash
   # Создаем .env из примера
   cp .env.example .env
   # При необходимости отредактируйте .env под свои порты
   ```

3. **Запустите инфраструктуру (БД):**
   ```bash
   docker compose up -d
   ```

### Через Docker (Рекомендуется)
Самый простой способ поднять всю инфраструктуру (БД, Redis, API, Worker, Flower):

1. **Запустите проект одной командой:**
   ```bash
   make build
   ```
2. **Доступные интерфейсы:**
   - **API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Celery Monitor (Flower):** [http://localhost:5555](http://localhost:5555)

### Локальная разработка
Если вы хотите запустить проект вне контейнеров:
```bash
poetry install
make up          # Поднимет только Postgres и Redis в Docker
make migrate     # Применит миграции БД
make run         # Запустит FastAPI сервер
```

#### Запуск Frontend (Vite)
Фронтенд находится в папке `frontend`. Для работы требуется [Node.js](https://nodejs.org/).
```bash
cd frontend
npm install      # Установка зависимостей
npm run dev      # Запуск сервера разработки
```

## 🛠 Администрирование
Для управления системой и создания первого администратора используйте CLI. Это безопаснее, чем открывать такие эндпоинты в публичном API.

### Создание администратора
Выполните команду внутри работающего контейнера или локально (если настроено окружение):
```bash
# Через Docker (рекомендуется)
docker exec pyflow_app python src/cli.py create-admin admin@oms.com superpassword
```
После создания вы сможете зайти в **Admin Panel** в веб-интерфейсе.
---
