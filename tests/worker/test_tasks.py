from src.worker.tasks import generate_invoice_pdf, send_order_confirmation


def test_send_order_confirmation_logic():
    """
    Тестируем логику задачи БЕЗ реального Celery/Redis.
    Метод .apply() запускает задачу синхронно в текущем процессе.
    """
    order_id = 1
    email = "worker_test@example.com"
    amount = "500.00"

    # .apply() возвращает EagerResult
    result = send_order_confirmation.apply(args=(order_id, email, amount))

    assert result.status == "SUCCESS"
    assert result.result == f"Email sent to {email}"


def test_generate_invoice_pdf_logic():
    """Проверка генерации PDF."""
    result = generate_invoice_pdf.apply(args=(99,))

    assert result.status == "SUCCESS"
    assert result.result == "PDF generated"
