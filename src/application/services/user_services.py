from typing import Optional, List
from src.domain.entities.user import UserCreate, UserUpdate
from src.infrastructure.db.model.user_model import User as SAUser
from src.infrastructure.security import PasswordHelper
from src.domain.interfaces.abstract_repository import AbstractRepository
from src.infrastructure.config.logger_config import setup_logger

logger = setup_logger(__name__)


class UserService:
    def __init__(self, user_repo: AbstractRepository[SAUser]):
        self.repo = user_repo
        logger.debug("UserService успешно инициализирован.")

    async def create_user(self, user_data: UserCreate) -> SAUser:
        logger.info(f"Запрос на создание нового пользователя: login='{user_data.login}'")

        try:
            user_dict = user_data.model_dump(exclude={'password'})
            hashed_pw = PasswordHelper.hash_password(user_data.password)

            new_user_sa = SAUser(
                login=user_data.login,
                hashed_password=hashed_pw,
                role=user_data.role,
                branch=user_data.branch,
                is_active=True
            )

            created_user = await self.repo.add(new_user_sa)
            await self.repo.session.commit()

            logger.info(f"Пользователь создан успешно: ID={created_user.id}, login='{created_user.login}'")
            return created_user
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя '{user_data.login}': {e}", exc_info=True)
            await self.repo.session.rollback()
            raise

    async def get_user_by_id(self, user_id: int) -> Optional[SAUser]:
        logger.debug(f"Запрос данных пользователя: ID={user_id}")
        user = await self.repo.get_by_id(user_id)

        if user is None:
            logger.warning(f"Пользователь не найден: ID={user_id}")
        else:
            logger.debug(f"Данные пользователя получены: ID={user_id}")
        return user

    async def get_all_users(self) -> List[SAUser]:
        logger.info("Запрос списка всех активных пользователей.")
        try:
            users = await self.repo.list()
            logger.info(f"Успешно получено пользователей: {len(users)}")
            return users
        except Exception as e:
            logger.error(f"Не удалось получить список пользователей: {e}")
            raise

    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[SAUser]:
        logger.info(f"Запрос на обновление пользователя: ID={user_id}")

        existing_user = await self.repo.get_by_id(user_id)
        if existing_user is None:
            logger.warning(f"Обновление невозможно: пользователь ID={user_id} не найден.")
            return None

        try:
            update_data = user_data.model_dump(exclude_unset=True)

            fields_to_update = list(update_data.keys())
            logger.debug(f"Обновляемые поля для ID={user_id}: {fields_to_update}")

            if "password" in update_data:
                raw_password = update_data.pop("password")
                existing_user.hashed_password = PasswordHelper.hash_password(raw_password)
                logger.debug(f"Пароль для ID={user_id} обновлен (хеширован).")

            for key, value in update_data.items():
                setattr(existing_user, key, value)

            updated_object = await self.repo.update(existing_user)
            await self.repo.session.commit()

            logger.info(f"Данные пользователя ID={user_id} успешно сохранены в БД.")
            return updated_object
        except Exception as e:
            logger.error(f"Критическая ошибка при обновлении ID={user_id}: {e}", exc_info=True)
            await self.repo.session.rollback()
            raise

    async def soft_delete_user(self, user_id: int) -> bool:
        logger.warning(f"Запущена процедура мягкого удаления: ID={user_id}")

        try:
            is_deleted = await self.repo.delete(user_id)
            await self.repo.session.commit()

            if is_deleted:
                logger.info(f"Пользователь ID={user_id} успешно помечен как удаленный.")
            else:
                logger.warning(f"Не удалось удалить ID={user_id}: запись не найдена или уже удалена.")

            return is_deleted
        except Exception as e:
            logger.error(f"Ошибка при удалении ID={user_id}: {e}", exc_info=True)
            await self.repo.session.rollback()
            raise