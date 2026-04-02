import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import (create_access_token, create_refresh_token, hash_password,
                      verify_password)
from app.config import ALGORITHM, SECRET_KEY
from app.db_depends import get_async_db
from app.models.users import User as UserModel
from app.schemas import RefreshTokenRequest
from app.schemas import User as UserSchema
from app.schemas import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_async_db),
) -> UserSchema:
    """
    Регистрирует нового пользователя с ролью 'buyer' или 'seller'.
    """

    # Проверка уникальности email
    result = await db.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Создание объекта пользователя с хешированным паролем
    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role,
    )

    # Добавление в сессию и сохранение в базе
    db.add(db_user)
    await db.commit()
    return db_user


@router.get("/", response_model=list[UserSchema])
async def get_all_users(db: AsyncSession = Depends(get_async_db)):
    """Получает все пользователей."""
    users_result = await db.scalars(select(UserModel))
    users = users_result.all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return users


@router.delete("/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_async_db)):
    result = await db.scalars(select(UserModel).where(UserModel.id == user_id))
    user = result.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")

    user.is_active = False
    await db.commit()
    return user


@router.post("/token")
async def logit(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    """Аутентифицирует пользователя и возвращает JWT с email, role и id."""
    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == form_data.username,
            UserModel.is_active == True,    # noqa
        ),
    )
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    data = {"sub": user.email, "role": user.role, "id": user.id}
    access_token = create_access_token(data=data)
    refresh_token = create_refresh_token(data=data)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token")
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """Обновляет refresh-token, принимая старый refresh-token в теле запроса"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    old_refresh_token = body.refresh_token
    try:
        pyload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = pyload.get("sub")
        token_type: str | None = pyload.get("token_type")
        if email is None or token_type != "refresh":
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(
        select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active == True,    # noqa
        ),
    )
    user = result.first()
    if user is None:
        raise credentials_exception

    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
    )
    return {"refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/access-token")
async def get_access_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
):
    """Возвращает access-token, принимая refresh-token в теле запроса"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    old_refresh_token = body.refresh_token

    try:
        pyload = jwt.decode(old_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = pyload.get("sub")
        token_type: str | None = pyload.get("token_type")
        if email is None or token_type != "refresh":
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True)
    )
    user = result.one_or_none()
    if user is None:
        raise credentials_exception
    
    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
    )
    return {"access_token": new_access_token, "token_type": "bearer"}