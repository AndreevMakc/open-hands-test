from abc import abstractmethod
from typing import List, Optional

from .base import BaseRepository
from ..entities.category import Category
from ..value_objects.common import EntityId
from ..value_objects.category import CategoryPath


class CategoryRepository(BaseRepository[Category]):
    """Category repository interface"""
    
    @abstractmethod
    async def get_all(self, include_inactive: bool = False) -> List[Category]:
        """Get all categories"""
        pass
    
    @abstractmethod
    async def get_by_parent_id(
        self, 
        parent_id: Optional[EntityId], 
        include_inactive: bool = False
    ) -> List[Category]:
        """Get categories by parent ID"""
        pass
    
    @abstractmethod
    async def get_tree(self, include_inactive: bool = False) -> List[Category]:
        """Get category tree"""
        pass
    
    @abstractmethod
    async def get_by_path(self, path: CategoryPath) -> Optional[Category]:
        """Get category by path"""
        pass
    
    @abstractmethod
    async def get_descendants(
        self, 
        category: Category, 
        include_inactive: bool = False
    ) -> List[Category]:
        """Get all descendants of category"""
        pass
    
    @abstractmethod
    async def has_children(self, category_id: EntityId) -> bool:
        """Check if category has children"""
        pass
    
    @abstractmethod
    async def has_products(self, category_id: EntityId) -> bool:
        """Check if category has products"""
        pass
    
    @abstractmethod
    async def get_root_categories(self, include_inactive: bool = False) -> List[Category]:
        """Get root categories"""
        pass