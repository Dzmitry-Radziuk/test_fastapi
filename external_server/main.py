import asyncio
import random

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(
    title='Внешний Эмулятор Кадастровой Службы',
    description='Дополнительный сервис для имитации задержек внешнего сервера (ТЗ Доп. задание №1)',
)


class ExternalCadastreRequest(BaseModel):
    """Схема входящих данных от главного сервиса для эмулятора."""

    cadastral_number: str
    latitude: float
    longitude: float


@app.post('/result')
async def get_cadastre_result(data: ExternalCadastreRequest):
    """Эмуляция долгой обработки запроса со случайным результатом."""
    delay = random.randint(5, 15)
    await asyncio.sleep(delay)

    server_status = random.choice([True, False])

    return {'status': server_status}
