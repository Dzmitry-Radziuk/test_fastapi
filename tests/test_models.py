from app.models import CadastreQuery, User


def test_user_model_creation():
    """Проверка корректности инициализации полей модели User."""
    user = User(
        email='model_test@mail.ru', hashed_password='hashed_string_123'
    )
    assert user.email == 'model_test@mail.ru'
    assert user.hashed_password == 'hashed_string_123'


def test_cadastre_query_repr():
    """Проверка строкового представления модели CadastreQuery."""
    query = CadastreQuery(
        cadastral_number='77:01:0001001:1234',
        latitude=55.7558,
        longitude=37.6173,
        result=True,
        user_id=1,
    )
    assert (
        repr(query)
        == '<CadastreQuery(number=77:01:0001001:1234, result=True)>'
    )
