from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

from ..entities.base import BaseEntity
from ..value_objects.common import EntityId

T = TypeVar('T', bound=BaseEntity)


class BaseRepository(ABC, Generic[T]):
    """Base repository interface"""
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: EntityId) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: EntityId) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def exists(self, entity_id: EntityId) -> bool:
        """Check if entity exists"""
        pass