import logging
from collections.abc import MutableMapping  # noqa: F401
from typing import Any

import structlog
from asgi_correlation_id import correlation_id


def setup_logging() -> None:
    """Настройка JSON логгирования для Enterprise."""

    # Настраиваем structlog
    structlog.configure(
        processors=[
            # Добавляем таймстемп
            structlog.processors.TimeStamper(fmt="iso"),
            # Добавляем уровень лога (INFO, ERROR)
            structlog.processors.add_log_level,
            # Внедряем Correlation ID (ID запроса) в каждый лог
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                }
            ),
            # Динамически добавляем request_id из контекста (созданный middleware)
            merge_correlation_id,
            # Превращаем в JSON
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def merge_correlation_id(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Функция для извлечения request_id и добавления его в JSON лог."""
    req_id = correlation_id.get()
    if req_id:
        event_dict["request_id"] = req_id
    return event_dict
