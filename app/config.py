from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс настроек проекта."""

    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = 'postgres'
    DB_NAME: str = 'cadastre_db'

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_TTL: int = 600

    EXTERNAL_SERVER_URL: str = 'http://external_web:8001/result'

    SECRET_KEY: str = 'SUPER_SECRET_KEY_KAD_35_PRO'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """Формирует строку подключения для asyncpg"""
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
