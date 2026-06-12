import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth_utils import create_access_token, hash_password, verify_password
from app.config import settings
from app.database import get_db, redis_client
from app.dependencies import get_current_user
from app.models import CadastreQuery, User
from app.schemas import (
    CadastreHistoryResponse,
    CadastreRequest,
    CadastreResponse,
    TokenSchema,
    UserAuthSchema,
)


router = APIRouter(tags=['Cadastre & Auth'])


@router.post(
    '/auth/register',
    status_code=status.HTTP_201_CREATED,
    summary='Регистрация нового пользователя',
)
async def register(
    user_data: UserAuthSchema, db: AsyncSession = Depends(get_db)
):
    """Регистрация нового пользователя в системе с уникальным email."""
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пользователь с таким email уже зарегистрирован',
        )

    hashed_pwd = hash_password(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_pwd)
    db.add(new_user)
    await db.commit()
    return {'message': 'Пользователь успешно зарегистрирован'}


@router.post(
    '/auth/login',
    response_model=TokenSchema,
    summary='Вход в систему (получение токена)',
)
async def login(
    user_data: UserAuthSchema,
    db: AsyncSession = Depends(get_db),
):
    """Аутентификация пользователя и выдача JWT-токена доступа."""
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(
        user_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный email или пароль',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token = create_access_token(data={'sub': str(user.id)})
    return TokenSchema(access_token=access_token)


@router.get('/ping', summary='Проверка работоспособности сервера')
async def ping():
    """Проверка доступности и старта сервера."""
    return {'status': 'ok', 'message': 'Сервер успешно запустился!'}


@router.post(
    '/query',
    response_model=CadastreResponse,
    summary='Отправить кадастровый номер на проверку',
)
async def process_query(
    request_data: CadastreRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отправка кадастрового номера на эмулятор проверки с кэшированием в Redis."""
    cad_number = request_data.cadastral_number

    try:
        cached_result = await redis_client.get(cad_number)
        if cached_result is not None:
            result_bool = cached_result.lower() == 'true'
            return CadastreResponse(
                cadastral_number=cad_number, result=result_bool
            )
    except Exception:
        pass

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                settings.EXTERNAL_SERVER_URL,
                json=request_data.model_dump(),
                timeout=70.0,
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail='Внешний сервер вернул ошибку',
                )
            server_result = response.json().get('status')
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Не удалось связаться с внешнем сервером',
            )

    new_query = CadastreQuery(
        cadastral_number=cad_number,
        latitude=request_data.latitude,
        longitude=request_data.longitude,
        result=server_result,
        user_id=current_user.id,
    )
    db.add(new_query)
    await db.commit()

    try:
        await redis_client.set(
            name=cad_number, value=str(server_result), ex=settings.REDIS_TTL
        )
    except Exception:
        pass

    return CadastreResponse(cadastral_number=cad_number, result=server_result)


@router.get(
    '/history',
    response_model=list[CadastreHistoryResponse],
    summary='Получить историю запросов текущего пользователя',
)
async def get_history(
    cadastral_number: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получение списка прошедших кадастровых запросов авторизованного пользователя."""
    query = (
        select(CadastreQuery)
        .where(CadastreQuery.user_id == current_user.id)
        .order_by(CadastreQuery.created_at.desc())
    )

    if cadastral_number:
        query = query.where(CadastreQuery.cadastral_number == cadastral_number)

    result = await db.execute(query)
    return result.scalars().all()
