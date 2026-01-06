import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from src.application import UserService
from src.application import AuthService

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.session = AsyncMock()
    return repo

@pytest.fixture
def auth_service(mock_repo):
    return AuthService(user_repo=mock_repo)

@pytest.fixture
def user_service(mock_repo):
    return UserService(user_repo=mock_repo)

@pytest.fixture
def mock_grpc_context():
    context = AsyncMock()
    return context