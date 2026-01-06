import pytest
from unittest.mock import MagicMock
from src.domain.entities.user import UserCreate, UserUpdate, UserRole
from src.infrastructure.db.model.user_model import User as SAUser


@pytest.mark.asyncio
class TestUserService:

    async def test_create_user_success(self, user_service, mock_repo):
        user_data = UserCreate(
            login="new_guy",
            password="password123",
            role=UserRole.USER
        )
        mock_repo.add.side_effect = lambda u: u

        result = await user_service.create_user(user_data)

        assert result.login == "new_guy"
        assert result.is_active is True
        mock_repo.add.assert_called_once()
        mock_repo.session.commit.assert_called_once()

    async def test_get_user_by_id_not_found(self, user_service, mock_repo):
        mock_repo.get_by_id.return_value = None

        result = await user_service.get_user_by_id(999)

        assert result is None

    async def test_update_user_password(self, user_service, mock_repo):
        existing_user = SAUser(id=1, login="old", hashed_password="old_hash")
        mock_repo.get_by_id.return_value = existing_user
        mock_repo.update.return_value = existing_user

        update_data = UserUpdate(password="new_password")

        updated_user = await user_service.update_user(1, update_data)

        assert updated_user.hashed_password != "old_hash"
        mock_repo.session.commit.assert_called_once()

    async def test_soft_delete_success(self, user_service, mock_repo):
        mock_repo.delete.return_value = True

        success = await user_service.soft_delete_user(1)

        assert success is True
        mock_repo.delete.assert_called_with(1)
        mock_repo.session.commit.assert_called_once()