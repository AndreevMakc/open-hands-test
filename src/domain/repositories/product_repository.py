"""
Product repository interface

Abstract base class for product repository implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple

from ..entities.product import Product, ProductStatus
from ..value_objects.common import EntityId
from ..value_objects.product import SKU


class ProductRepository(ABC):
    """Abstract repository for product operations"""
    
    @abstractmethod
    async def create(self, product: Product) -> Product:
        """Create a new product"""
        pass
    
    @abstractmethod
    async def get_by_id(self, product_id: EntityId) -> Optional[Product]:
        """Get product by ID"""
        pass
    
    @abstractmethod
    async def get_by_sku(self, sku: SKU) -> Optional[Product]:
        """Get product by SKU"""
        pass
    
    @abstractmethod
    async def update(self, product: Product) -> Product:
        """Update an existing product"""
        pass
    
    @abstractmethod
    async def delete(self, product_id: EntityId) -> bool:
        """Delete product by ID"""
        pass
    
    @abstractmethod
    async def list_with_filters(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """List products with filters and pagination"""
        pass
    
    @abstractmethod
    async def search(
        self,
        criteria: Dict[str, Any],
        page: int = 1,
        size: int = 20,
        sort_by: str = "relevance",
        sort_order: str = "desc"
    ) -> Tuple[List[Product], int]:
        """Advanced product search"""
        pass
    
    @abstractmethod
    async def get_by_category_ids(self, category_ids: List[EntityId]) -> List[Product]:
        """Get products by category IDs"""
        pass
    
    @abstractmethod
    async def bulk_delete(self, product_ids: List[EntityId]) -> int:
        """Bulk delete products"""
        pass
    
    @abstractmethod
    async def bulk_update_status(self, product_ids: List[EntityId], status: ProductStatus) -> int:
        """Bulk update product status"""
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """Get product statistics"""
        pass