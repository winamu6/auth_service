from typing import List, Optional
from src.domain.interfaces.abstract_repository import AbstractRepository
from src.domain.entities.user import UserCreate, UserUpdate
from src.infrastructure.db.model.user_model import User as SAUser
from src.infrastructure import PasswordHelper
from src.infrastructure import base_logger as logger


class UserService:

    def __init__(self, user_repo: AbstractRepository[SAUser]):
        self.repo = user_repo
        logger.info("UserService инициализирован.")

    async def create_user(self, user_data: UserCreate) -> SAUser:
        logger.info(f"Начато создание user: {user_data.login}")

        user_dict = user_data.model_dump(exclude={'password'})

        hashed_pw = PasswordHelper.hash_password(user_data.password)
        new_user_sa = SAUser(**user_dict, hashed_password=hashed_pw)

        created_user = await self.repo.add(new_user_sa)
        await self.repo.session.commit()
        return created_user

    async def get_user_by_id(self, user_id: int) -> Optional[SAUser]:
        logger.debug(f"Поиск user с ID: {user_id}")

        obj = await self.repo.get_by_id(user_id)

        if obj is None:
            logger.warning(f"User с ID {user_id} не найден или удален.")
        else:
            logger.debug(f"User с ID {user_id} найден.")

        return obj

    async def get_all_users(self) -> List[SAUser]:
        logger.info("Получение списка всех активных пользователей.")

        objects_list = await self.repo.list()

        logger.info(f"Найдено {len(objects_list)} активных пользователей.")
        return objects_list

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[SAUser]:
        logger.info(f"Начато обновление user с ID: {user_id}")

        existing_user = await self.repo.get_by_id(user_id)
        if existing_user is None:
            return None

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            raw_password = update_data.pop("password")
            existing_user.hashed_password = PasswordHelper.hash_password(raw_password)

        for key, value in update_data.items():
            setattr(existing_user, key, value)

        updated_object = await self.repo.update(existing_user)
        await self.repo.session.commit()

        logger.info(f"Пароль/данные User ID {user_id} успешно обновлены.")
        return updated_object

    async def soft_delete_user(self, user_id: int) -> bool:
        logger.warning(f"Начато мягкое удаление user с ID: {user_id}")

        is_deleted = await self.repo.delete(user_id)

        await self.repo.session.commit()

        if is_deleted:
            logger.info(f"User с ID {user_id} успешно мягко удален.")
        else:
            logger.warning(f"Не удалось найти user с ID {user_id} для удаления.")

        return is_deleted