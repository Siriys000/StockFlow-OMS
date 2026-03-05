# Архитектура StockFlow OMS

## Общая схема

```mermaid
graph TD
    User["Client"] --> API["FastAPI Routes"]
    API --> Service["Domain Services / Use Cases"]
    Service --> Repository["Repositories / Infrastructure"]
    Repository --> DB[("(PostgreSQL)")]
    Service --> Tasks["Background Tasks / Redis"]
```

## Структура папок
- `src/app/` — Инициализация FastAPI, глобальные зависимости (DI), мидлвары.
- `src/core/` — Глобальные конфиги, общие исключения, базовые классы БД.
- `src/modules/` — Бизнес-логика, разбитая по контекстам (Auth, Orders, Inventory).
- `src/utils/` — Вспомогательные скрипты и утилиты.
