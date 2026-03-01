import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import HTTPException, status

from src.infrastructure.security import PasswordHelper
from src.domain.entities.login import Token, LoginRequest
from src.infrastructure.config.settings import settings
from src.infrastructure.config.logger_config import setup_logger

logger = setup_logger(__name__)


class AuthService:
    def __init__(self, user_repo):
        self.repo = user_repo

    async def authenticate_user(self, login_data: LoginRequest) -> Token:
        logger.info(f"Запрос на аутентификацию: login='{login_data.login}'")

        user = await self.repo.get_by_login(login_data.login)

        if not user or not PasswordHelper.verify_password(login_data.password, user.hashed_password):
            logger.warning(f"Провал аутентификации для '{login_data.login}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )

        return await self._create_token_pair(user)

    async def refresh_access_token(self, refresh_token: str) -> Token:
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

            user_login = payload.get("sub")
            user = await self.repo.get_by_login(user_login)

            if not user or user.refresh_token != refresh_token:
                logger.warning(f"Попытка использования невалидного refresh токена для {user_login}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token is invalid or expired"
                )

            logger.info(f"Обновление сессии для пользователя: {user_login}")
            return await self._create_token_pair(user)

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    async def _create_token_pair(self, user) -> Token:
        access_token = self.create_token(
            data={
                "sub": user.login,
                "role": user.role.value,
                "user_id": user.id,
                "branch": user.branch,
                "type": "access"
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = self.create_token(
            data={
                "sub": user.login,
                "type": "refresh"
            },
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        await self.repo.update_refresh_token(user.id, refresh_token)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    def create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": int(expire.timestamp())})

        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    async def validate_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "access":
                raise jwt.PyJWTError()

            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    async def logout_user(self, user_id: int):
        success = await self.repo.revoke_user_tokens(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        logger.info(f"Сессия пользователя {user_id} успешно аннулирована.")
        return True