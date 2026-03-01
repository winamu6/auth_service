from typing import Optional, List, Any
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.abstract_repository import AbstractRepository
from src.infrastructure.db.model.user_model import User as SAUser
from src.infrastructure.config.logger_config import setup_logger

logger = setup_logger(__name__)

class SQLAlchemyUserRepository(AbstractRepository[SAUser]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, entity: SAUser) -> SAUser:
        logger.info(f"Добавление нового пользователя в сессию: login={entity.login}")
        try:
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except Exception as e:
            logger.error(f"Ошибка SQLAlchemy при добавлении: {e}")
            raise

    async def get_by_id(self, entity_id: int) -> Optional[SAUser]:
        logger.debug(f"Поиск пользователя по ID: {entity_id}")
        stmt = select(SAUser).where(SAUser.id == entity_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none() # Сначала получаем результат

        if not user:
            logger.warning(f"Пользователь с ID {entity_id} не найден")
            return None
        return user

    async def get_by_login(self, login: str) -> Optional[SAUser]:
        logger.debug(f"Поиск активного пользователя по логину: {login}")
        stmt = select(SAUser).where(SAUser.login == login, SAUser.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(self, **filters: Any) -> List[SAUser]:
        logger.debug(f"Запрос списка пользователей с фильтрами: {filters}")
        try:
            stmt = select(SAUser).filter_by(**filters)
            result = await self.session.execute(stmt)
            users = list(result.scalars().all())
            return users
        except Exception as e:
            logger.error(f"Ошибка при получении списка: {e}")
            raise

    async def update(self, entity: SAUser) -> SAUser:
        logger.info(f"Обновление состояния объекта пользователя ID: {entity.id}")
        try:
            await self.session.merge(entity)
            await self.session.flush()
            return entity
        except Exception as e:
            logger.error(f"Ошибка при merge пользователя ID {entity.id}: {e}")
            raise

    async def update_refresh_token(self, user_id: int, token: Optional[str]) -> None:
        logger.info(f"Обновление refresh токена для пользователя ID: {user_id}")
        try:
            stmt = (
                update(SAUser)
                .where(SAUser.id == user_id)
                .values(refresh_token=token)
            )
            await self.session.execute(stmt)
            await self.session.flush()
        except Exception as e:
            logger.error(f"Ошибка при обновлении refresh токена ID {user_id}: {e}")
            raise

    async def delete(self, entity_id: int) -> bool:
        logger.warning(f"Выполнение Soft Delete для ID: {entity_id}")
        try:
            stmt = (
                update(SAUser)
                .where(SAUser.id == entity_id)
                .values(is_active=False)
            )
            result = await self.session.execute(stmt)
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при soft delete ID {entity_id}: {e}")
            raise

    async def revoke_user_tokens(self, user_id: int) -> bool:
        logger.warning(f"Админ-панель: отзыв токенов для пользователя ID: {user_id}")
        try:
            stmt = (
                update(SAUser)
                .where(SAUser.id == user_id)
                .values(refresh_token=None)
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            return result.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при отзыве токена для ID {user_id}: {e}")
            raise

    async def get_by_branch(self, branch: int) -> List[SAUser]:
        logger.debug(f"Поиск пользователей филиала: {branch}")
        stmt = select(SAUser).where(SAUser.branch == branch, SAUser.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())