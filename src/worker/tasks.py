import logging
import time

from src.worker.celery_app import celery

# Настраиваем логгер для воркера
logger = logging.getLogger(__name__)


# Библиотека Celery не имеет аннотаций типов,
# и Mypy "теряет" контекст функции при использовании декоратора @celery.task


@celery.task(name="tasks.send_order_confirmation")  # type: ignore[untyped-decorator]
def send_order_confirmation(order_id: int, user_email: str, total_amount: str) -> str:
    """
    Фоновая задача отправки Email.
    Важно: Celery-задачи в Python обычно СИНХРОННЫЕ (не async def).
    """
    logger.info(f"🚀 [WORKER] Начинаю отправку email для заказа #{order_id} на {user_email}")

    # Имитируем сетевую задержку отправки письма (2 секунды)
    # Если бы мы делали это в FastAPI, клиент ждал бы ответа API 2 лишние секунды!
    time.sleep(2)

    logger.info(f"✅ [WORKER] Email успешно отправлен! Сумма: {total_amount}")

    return f"Email sent to {user_email}"


@celery.task(name="tasks.generate_invoice_pdf")  # type: ignore[untyped-decorator]
def generate_invoice_pdf(order_id: int) -> str:
    """
    Имитация тяжелой задачи генерации PDF.
    """
    logger.info(f"📄 [WORKER] Генерирую PDF-накладную для заказа #{order_id}...")
    time.sleep(3)  # "Рисуем" PDF
    logger.info(f"✅ [WORKER] PDF для заказа #{order_id} сгенерирован и сохранен на S3!")
    return "PDF generated"
