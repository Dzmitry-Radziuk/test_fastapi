from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """Модель пользователя системы."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    queries: Mapped[list['CadastreQuery']] = relationship(
        back_populates='user'
    )


class CadastreQuery(Base):
    """Модель истории кадастровых запросов пользователя."""

    __tablename__ = 'cadastre_queries'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cadastral_number: Mapped[str] = mapped_column(
        String(50), index=True, nullable=False
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    result: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'), nullable=False
    )
    user: Mapped['User'] = relationship(back_populates='queries')

    def __repr__(self) -> str:
        return f'<CadastreQuery(number={self.cadastral_number}, result={self.result})>'
