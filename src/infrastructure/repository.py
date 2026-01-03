from typing import Optional, List, Any
from sqlalchemy import select, update

from src.domain.interfaces.abstract_repository import AbstractRepository
from src.infrastructure.db.model.user_model import User as SAUser
from src.infrastructure.config.logger_config import setup_logger


class SQLAlchemyUserRepository(AbstractRepository[SAUser]):
    logger = setup_logger(__name__)

    def __init__(self, session):
        self.session = session

    async def add(self, entity: SAUser) -> SAUser:
        self.logger.info(f"Добавление пользователя: {entity.login}")
        try:
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении: {e}", exc_info=True)
            raise

        except Exception as e:
            self.logger.error(f"Ошибка при добавлении: {e}", exc_info=True)
            raise


    async def get_by_login(self, login: str) -> Optional[SAUser]:
        self.logger.debug(f"Поиск пользователя по логину: {login}")
        stmt = select(SAUser).where(SAUser.login == login, SAUser.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    async def list(self, **filters: Any) -> List[SAUser]:
        self.logger.debug(f"Запрос списка user с фильтрами: {filters}")

        filters.setdefault("deleted", False)

        stmt = (
            select(SAUser)
            .filter_by(**filters)
        )

        result = await self.session.execute(stmt)
        return list(result.scalars().all())


    async def update(self, entity: SAUser) -> SAUser:
        self.logger.info(f"Обновление user ID: {entity.id}")
        await self.session.merge(entity)
        await self.session.flush()

        return await self.get_by_id(entity.id)


    async def get_by_id(self, entity_id: int) -> Optional[SAUser]:
        self.logger.debug(f"Поиск объекта с ID: {entity_id}")
        stmt = (
            select(SAUser)
            .where(SAUser.id == entity_id, SAUser.is_active == False)
        )

        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return user

        self.logger.warning(f"Объект ID {entity_id} не найден или удален.")
        return None


    async def delete(self, entity_id: int) -> bool:
        self.logger.warning(f"Мягкое удаление объекта ID: {entity_id}")

        stmt = (
            update(SAUser)
            .where(SAUser.id == entity_id, SAUser.is_active == False)
            .values(deleted=True)
        )

        result = await self.session.execute(stmt)
        return result.rowcount > 0