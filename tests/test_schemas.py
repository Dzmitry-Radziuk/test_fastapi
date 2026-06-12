import pytest
from pydantic import ValidationError

from app.schemas import CadastreRequest, UserAuthSchema


def test_cadastre_request_valid():
    """Проверка валидации корректных данных в схеме CadastreRequest."""
    data = {
        'cadastral_number': '77:01:0001001:1234',
        'latitude': 55.7558,
        'longitude': 37.6173,
    }
    request = CadastreRequest(**data)
    assert request.cadastral_number == '77:01:0001001:1234'
    assert request.latitude == 55.7558


@pytest.mark.parametrize(
    'lat, lon',
    [(95.0, 37.6173), (-95.0, 37.6173), (55.7558, 185.0), (55.7558, -185.0)],
)
def test_cadastre_request_invalid_coordinates(lat, lon):
    """Проверка генерации ошибки при выходе координат за допустимые границы."""
    data = {
        'cadastral_number': '77:01:0001001:1234',
        'latitude': lat,
        'longitude': lon,
    }
    with pytest.raises(ValidationError):
        CadastreRequest(**data)


def test_user_auth_schema_invalid_email():
    """Проверка валидации некорректного формата email в схеме авторизации."""
    with pytest.raises(ValidationError):
        UserAuthSchema(email='not-an-email', password='password123')


def test_user_auth_schema_short_password():
    """Проверка валидации слишком короткого пароля в схеме авторизации."""
    with pytest.raises(ValidationError):
        UserAuthSchema(email='test@mail.ru', password='123')
