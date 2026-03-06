from celery import Celery

from src.core.config import settings

# Инициализируем Celery приложение
celery = Celery(
    "pyflow_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    # Указываем, в каких модулях Celery должен искать задачи (@celery.task)
    include=["src.worker.tasks"],
)

# Настройки Celery
celery.conf.update(
    # Задачи всегда должны выполняться в порядке очереди (FIFO)
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Если воркер упал, задача вернется в очередь (надежность)
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)
