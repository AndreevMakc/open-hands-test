"""
Attribute repository interface

Abstract base class for attribute repository implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple

from ..entities.attribute import Attribute
from ..value_objects.common import EntityId


class AttributeRepository(ABC):
    """Abstract repository for attribute operations"""
    
    @abstractmethod
    async def create(self, attribute: Attribute) -> Attribute:
        """Create a new attribute"""
        pass
    
    @abstractmethod
    async def get_by_id(self, attribute_id: EntityId) -> Optional[Attribute]:
        """Get attribute by ID"""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Attribute]:
        """Get attribute by name"""
        pass
    
    @abstractmethod
    async def update(self, attribute: Attribute) -> Attribute:
        """Update an existing attribute"""
        pass
    
    @abstractmethod
    async def delete(self, attribute_id: EntityId) -> bool:
        """Delete attribute by ID"""
        pass
    
    @abstractmethod
    async def list_with_filters(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = 20,
        sort_by: str = "display_order",
        sort_order: str = "asc"
    ) -> Tuple[List[Attribute], int]:
        """List attributes with filters and pagination"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Attribute]:
        """Get all attributes"""
        pass
    
    @abstractmethod
    async def get_by_category(self, category_id: EntityId) -> List[Attribute]:
        """Get attributes assigned to a category"""
        pass
    
    @abstractmethod
    async def assign_to_category(
        self,
        category_id: EntityId,
        attribute_ids: List[EntityId],
        inherit_to_children: bool = False
    ) -> List[Any]:
        """Assign attributes to a category"""
        pass
    
    @abstractmethod
    async def get_usage_count(self, attribute_id: EntityId) -> int:
        """Get number of products using this attribute"""
        pass
    
    @abstractmethod
    async def get_categories_count(self, attribute_id: EntityId) -> int:
        """Get number of categories using this attribute"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get attribute statistics"""
        pass