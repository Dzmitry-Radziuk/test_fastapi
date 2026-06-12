from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CadastreRequest(BaseModel):
    """Схема входящего запроса на проверку кадастрового номера."""

    cadastral_number: str = Field(
        ...,
        description='Кадастровый номер участка',
        examples=['77:01:0001001:1234'],
    )
    latitude: float = Field(
        ..., description='Широта', ge=-90.0, le=90.0, examples=[55.7558]
    )
    longitude: float = Field(
        ..., description='Долгота', ge=-180.0, le=180.0, examples=[37.6173]
    )


class CadastreResponse(BaseModel):
    """Схема ответа на одиночный запрос проверки."""

    cadastral_number: str
    result: bool


class CadastreHistoryResponse(BaseModel):
    """Схема для вывода записи из истории запросов пользователя."""

    id: int
    cadastral_number: str
    latitude: float
    longitude: float
    result: bool
    created_at: datetime

    model_config = {'from_attributes': True}


class UserAuthSchema(BaseModel):
    """Схема для регистрации и аутентификации пользователя."""

    email: EmailStr = Field(..., examples=['user@example.com'])
    password: str = Field(..., min_length=6, examples=['secret123'])


class TokenSchema(BaseModel):
    """Схема ответа при успешной аутентификации с JWT-токеном."""

    access_token: str
    token_type: str = 'bearer'


class TokenData(BaseModel):
    """Схема полезной нагрузки (payload) JWT-токена."""

    user_id: int | None = None
