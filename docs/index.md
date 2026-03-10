# StockFlow OMS
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**StockFlow OMS** — это проект системы управления заказами, разработанный для демонстрации бэкенд-разработки на Python.

### 🎯 Цель проекта
Цель репозитория — применение промышленного стека технологий и архитектурных паттернов в бизнес-задаче.

### 🛡 Что здесь реализовано (Production Standards):
- **Type Safety:** Строгая типизация с Mypy (strict mode).
- **Architecture:** Модульный монолит с разделением ответственности.
- **Reliability:** Работа с конкурентностью в БД.
- **Testing:** Изолированные тесты с транзакционным роллбэком (Pytest + AsyncIO).
- **CI/CD:** Автоматизация проверок и контейнеризация.
- **Observability:** Структурное логирование и готовность к мониторингу.

### ⚠️ Ограничения (Disclaimer)
Проект является учебным полигоном (Sandbox). В нем упрощены некоторые аспекты (нет подходящей системы аудита, Kubernetes-манифестов и интеграции с внешними платежными шлюзами).

## 🛠 Технологический стек

- **Core:** Python 3.12, FastAPI
- **Database:** PostgreSQL 15, SQLAlchemy 2.0 (Async), Alembic
- **Infrastructure:** Docker Compose
- **Dev Tools:** Pytest, Ruff, Mypy, Pre-commit

## 🏗 Архитектура

Подробное описание архитектуры см. в [ARCHITECTURE.md](architecture.md).

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

4. **Установите зависимости и примените миграции:**
   ```bash
   poetry install
   poetry run alembic upgrade head
   ```

5. **Запустите сервер:**
   ```bash
   poetry run uvicorn src.main:app --reload
   ```
   Документация API будет доступна по адресу: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

6. **Запуск тестов:**
   ```bash
   poetry run pytest -v
   ```
---
