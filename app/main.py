from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa
from app.database import Base, engine
from app.router import router as cadastre_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения: создание таблиц в БД при запуске."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title='Сервис проверки кадастровых номеров',
    version='0.1.0',
    description='Тестовое задание для Backend разработчика',
    lifespan=lifespan,
)

app.include_router(cadastre_router)
