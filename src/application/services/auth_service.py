import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status

from src.infrastructure.security import PasswordHelper
from src.domain.entities.login import Token, LoginRequest
from src.infrastructure.config.settings import settings
from src.infrastructure import base_logger as logger


class AuthService:
    def __init__(self, user_repo):
        self.repo = user_repo

    async def authenticate_user(self, login_data: LoginRequest) -> Optional[Token]:
        logger.info(f"Попытка входа пользователя: {login_data.login}")

        user = await self.repo.get_by_login(login_data.login)

        if not user:
            logger.warning(f"Пользователь {login_data.login} не найден.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )

        if not PasswordHelper.verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Неверный пароль для пользователя: {login_data.login}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )

        access_token = self.create_access_token(
            data={"sub": user.login, "role": user.role.value, "user_id": user.id}
        )

        logger.info(f"Пользователь {user.login} успешно авторизован.")
        return Token(access_token=access_token, token_type="bearer")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    async def validate_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.PyJWTError:
            logger.error("Невалидный токен при проверке.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )