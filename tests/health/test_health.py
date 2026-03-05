async def test_healthcheck(client):
    """
    Проверяем, что API живо и база подключена.
    Фикстура 'client' внедряется автоматически из conftest.py.
    """
    response = await client.get("/health")

    # 1. Проверяем HTTP статус
    assert response.status_code == 200

    # 2. Проверяем тело ответа
    data = response.json()

    # Если статус не 'ok', pytest выведет сообщение с деталями ошибки из БД!
    assert data["status"] == "ok", f"Database error: {data.get('details')}"
    assert data["database"] == "connected"
