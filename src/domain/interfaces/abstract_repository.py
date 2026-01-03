from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')


class AbstractRepository(ABC, Generic[T]):

    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def add(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    async def list(self, **filters: Any) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        raise NotImplementedError