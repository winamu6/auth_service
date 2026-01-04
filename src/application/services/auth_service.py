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

    async def authenticate_user(self, login_data: LoginRequest) -> Optional[Token]:
        logger.info(f"Запрос на аутентификацию: login='{login_data.login}'")

        try:
            user = await self.repo.get_by_login(login_data.login)

            if not user:
                logger.warning(f"Аутентификация провалена: пользователь '{login_data.login}' не существует")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный логин или пароль"
                )

            if not PasswordHelper.verify_password(login_data.password, user.hashed_password):
                logger.warning(f"Аутентификация провалена: неверный пароль для '{login_data.login}'")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный логин или пароль"
                )

            access_token = self.create_access_token(
                data={"sub": user.login, "role": user.role.value, "user_id": user.id}
            )

            logger.info(f"Успешный вход: user_id={user.id}, login='{user.login}'")
            return Token(access_token=access_token, token_type="bearer")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Критическая ошибка при аутентификации '{login_data.login}': {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Внутренняя ошибка сервера"
            )

    def create_access_token(self, data: dict) -> str:
        logger.debug(f"Генерация JWT токена для: {data.get('sub')}")
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                settings.JWT_SECRET_KEY,
                algorithm=settings.JWT_ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Ошибка при кодировании JWT: {e}")
            raise

    async def validate_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            logger.debug(f"Токен валидирован для пользователя: {payload.get('sub')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Попытка использования просроченного токена")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.PyJWTError as e:
            logger.warning(f"Ошибка валидации токена: {type(e).__name__}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )