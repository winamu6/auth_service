from unittest.mock import MagicMock

import pytest
from datetime import timedelta
from fastapi import HTTPException
from src.domain.entities.login import LoginRequest
from src.infrastructure.security import PasswordHelper


@pytest.mark.asyncio
class TestAuthService:

    async def test_authenticate_user_success(self, auth_service, mock_repo):
        password = "secret_password"
        hashed = PasswordHelper.hash_password(password)

        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.login = "test_user"
        mock_user.hashed_password = hashed
        mock_user.role.value = "user"
        mock_user.branch = 123

        mock_repo.get_by_login.return_value = mock_user
        login_data = LoginRequest(login="test_user", password=password)

        token_data = await auth_service.authenticate_user(login_data)

        assert token_data.access_token is not None
        assert token_data.token_type == "bearer"
        mock_repo.update_refresh_token.assert_called_once()

    async def test_authenticate_user_wrong_password(self, auth_service, mock_repo):
        mock_user = MagicMock()
        mock_user.hashed_password = PasswordHelper.hash_password("correct_pass")
        mock_repo.get_by_login.return_value = mock_user

        login_data = LoginRequest(login="test_user", password="wrong_password")

        with pytest.raises(HTTPException) as exc:
            await auth_service.authenticate_user(login_data)
        assert exc.value.status_code == 401

    async def test_validate_token_success(self, auth_service):
        data = {"sub": "admin", "role": "admin", "user_id": 1, "branch": 1, "type": "access"}
        token = auth_service.create_token(data, timedelta(minutes=5))

        payload = await auth_service.validate_token(token)

        assert payload["sub"] == "admin"
        assert payload["type"] == "access"

    async def test_validate_token_expired(self, auth_service):
        token = auth_service.create_token({"type": "access"}, timedelta(seconds=-1))

        with pytest.raises(HTTPException) as exc:
            await auth_service.validate_token(token)
        assert "expired" in exc.value.detail