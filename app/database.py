import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=False)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей базы данных."""

    pass


async def get_db():
    """Генератор асинхронных сессий базы данных для зависимостей FastAPI."""
    async with async_session() as session:
        yield session


redis_client = aioredis.from_url(
    f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}',
    encoding='utf-8',
    decode_responses=True,
)
