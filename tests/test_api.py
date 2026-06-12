from datetime import datetime, timezone

import pytest
from httpx import AsyncClient


BASE_URL = 'http://localhost:8000'


@pytest.mark.asyncio
async def test_ping_endpoint():
    """Проверка доступности эндпоинта /ping и корректности его ответа."""
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get('/ping')

    assert response.status_code == 200
    assert response.json() == {
        'status': 'ok',
        'message': 'Сервер успешно запустился!',
    }


@pytest.mark.asyncio
async def test_auth_and_validation_flow():
    """Тестирование полной цепочки регистрации, валидации, логина и проверки прав доступа."""
    unique_id = int(datetime.now(timezone.utc).timestamp())
    test_email = f'pytest_user_{unique_id}@mail.ru'
    test_password = 'secure_password123'

    async with AsyncClient(base_url=BASE_URL) as ac:
        bad_reg = await ac.post(
            '/auth/register',
            json={'email': test_email, 'password': '123'},
        )
        assert bad_reg.status_code == 422

        reg_response = await ac.post(
            '/auth/register',
            json={'email': test_email, 'password': test_password},
        )
        assert reg_response.status_code == 201
        assert 'успешно зарегистрирован' in reg_response.json()['message']

        query_unauth = await ac.post(
            '/query',
            json={
                'cadastral_number': '77:01:0001001:1234',
                'latitude': 55.75,
                'longitude': 37.61,
            },
        )
        assert query_unauth.status_code == 401

        login_response = await ac.post(
            '/auth/login',
            json={'email': test_email, 'password': test_password},
        )
        assert login_response.status_code == 200

        token_data = login_response.json()
        assert 'access_token' in token_data
        assert token_data['token_type'] == 'bearer'
