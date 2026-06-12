import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Импортируем ваши настройки и базовый класс моделей
from app.config import settings
from app.database import Base


# Обязательно импортируем саму модель, чтобы Alembic «увидел» таблицу cadastre_queries


# Это объект конфигурации Alembic
config = context.config

# Настраиваем логирование, если файл конфигурации существует
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные наших моделей для автогенерации
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в "offline" режиме.

    Здесь нам не нужно живое соединение с базой, мы просто генерируем SQL-скрипт.
    """
    # Берем асинхронный URL из нашего синглтона настроек settings
    url = settings.DATABASE_URL_ASYNC
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Вспомогательный синхронный метод для применения миграций внутри контекста."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в асинхронном "online" режиме.

    Создаем асинхронный движок и связываем соединение с контекстом Alembic.
    """
    connectable = create_async_engine(
        settings.DATABASE_URL_ASYNC,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Так как Alembic внутри синхронный, запускаем миграции через run_sync
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Используем asyncio.run для запуска асинхронного онлайн-режима
    asyncio.run(run_migrations_online())
