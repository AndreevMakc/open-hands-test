"""
Category-specific caching service
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from .cache_service import CacheService
from .redis_client import RedisClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


class CategoryCacheService(CacheService):
    """Cache service for category operations"""
    
    def __init__(self, redis_client: RedisClient):
        super().__init__(redis_client, key_prefix="category")
        self.ttl_category = settings.cache_ttl_categories
        self.ttl_tree = settings.cache_ttl_category_tree
        self.ttl_attributes = settings.cache_ttl_category_attributes
    
    # Category caching
    async def get_category(self, category_id: UUID) -> Optional[Dict[str, Any]]:
        """Get category from cache"""
        key = f"cat:{category_id}"
        return await self.get(key)
    
    async def set_category(self, category_id: UUID, category_data: Dict[str, Any]) -> bool:
        """Cache category data"""
        key = f"cat:{category_id}"
        return await self.set(key, category_data, ttl=self.ttl_category)
    
    async def delete_category(self, category_id: UUID) -> int:
        """Remove category from cache"""
        key = f"cat:{category_id}"
        return await self.delete(key)
    
    # Category tree caching
    async def get_category_tree(self) -> Optional[List[Dict[str, Any]]]:
        """Get full category tree from cache"""
        return await self.get("tree:full")
    
    async def set_category_tree(self, tree_data: List[Dict[str, Any]]) -> bool:
        """Cache category tree"""
        return await self.set("tree:full", tree_data, ttl=self.ttl_tree)
    
    async def delete_category_tree(self) -> int:
        """Remove category tree from cache"""
        return await self.delete("tree:full")
    
    # Category children caching
    async def get_category_children(self, category_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """Get category children from cache"""
        key = f"children:{category_id}"
        return await self.get(key)
    
    async def set_category_children(
        self, 
        category_id: UUID, 
        children_data: List[Dict[str, Any]]
    ) -> bool:
        """Cache category children"""
        key = f"children:{category_id}"
        return await self.set(key, children_data, ttl=self.ttl_tree)
    
    async def delete_category_children(self, category_id: UUID) -> int:
        """Remove category children from cache"""
        key = f"children:{category_id}"
        return await self.delete(key)
    
    # Category path caching
    async def get_category_path(self, category_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """Get category path (breadcrumbs) from cache"""
        key = f"path:{category_id}"
        return await self.get(key)
    
    async def set_category_path(
        self, 
        category_id: UUID, 
        path_data: List[Dict[str, Any]]
    ) -> bool:
        """Cache category path"""
        key = f"path:{category_id}"
        return await self.set(key, path_data, ttl=self.ttl_tree)
    
    async def delete_category_path(self, category_id: UUID) -> int:
        """Remove category path from cache"""
        key = f"path:{category_id}"
        return await self.delete(key)
    
    # Category attributes caching
    async def get_category_attributes(self, category_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """Get category attributes from cache"""
        key = f"attrs:{category_id}"
        return await self.get(key)
    
    async def set_category_attributes(
        self, 
        category_id: UUID, 
        attributes_data: List[Dict[str, Any]]
    ) -> bool:
        """Cache category attributes"""
        key = f"attrs:{category_id}"
        return await self.set(key, attributes_data, ttl=self.ttl_attributes)
    
    async def delete_category_attributes(self, category_id: UUID) -> int:
        """Remove category attributes from cache"""
        key = f"attrs:{category_id}"
        return await self.delete(key)
    
    # Category list caching
    async def get_category_list(
        self, 
        page: int = 1, 
        size: int = 20, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get category list from cache"""
        filter_hash = self._hash_key(filters) if filters else "all"
        key = f"list:{page}:{size}:{filter_hash}"
        return await self.get(key)
    
    async def set_category_list(
        self,
        page: int,
        size: int,
        filters: Optional[Dict[str, Any]],
        list_data: Dict[str, Any]
    ) -> bool:
        """Cache category list"""
        filter_hash = self._hash_key(filters) if filters else "all"
        key = f"list:{page}:{size}:{filter_hash}"
        return await self.set(key, list_data, ttl=self.ttl_tree)
    
    # Cache invalidation methods
    async def invalidate_category(self, category_id: UUID) -> None:
        """Invalidate all cache entries for a category"""
        await self.delete_category(category_id)
        await self.delete_category_children(category_id)
        await self.delete_category_path(category_id)
        await self.delete_category_attributes(category_id)
        
        # Also invalidate tree cache as it might contain this category
        await self.delete_category_tree()
        
        # Clear category lists
        await self.clear_pattern("list:*")
        
        logger.info(f"Invalidated cache for category {category_id}")
    
    async def invalidate_category_tree(self) -> None:
        """Invalidate category tree and related caches"""
        await self.delete_category_tree()
        await self.clear_pattern("children:*")
        await self.clear_pattern("path:*")
        await self.clear_pattern("list:*")
        
        logger.info("Invalidated category tree cache")
    
    async def invalidate_category_attributes(self, category_id: UUID) -> None:
        """Invalidate category attributes cache"""
        await self.delete_category_attributes(category_id)
        logger.info(f"Invalidated attributes cache for category {category_id}")
    
    async def invalidate_all(self) -> None:
        """Invalidate all category caches"""
        await self.clear_pattern("*")
        logger.info("Invalidated all category caches")
    
    # Statistics and monitoring
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for categories"""
        all_keys = await self.keys("*")
        
        stats = {
            "total_keys": len(all_keys),
            "categories": len([k for k in all_keys if k.startswith("cat:")]),
            "trees": len([k for k in all_keys if k.startswith("tree:")]),
            "children": len([k for k in all_keys if k.startswith("children:")]),
            "paths": len([k for k in all_keys if k.startswith("path:")]),
            "attributes": len([k for k in all_keys if k.startswith("attrs:")]),
            "lists": len([k for k in all_keys if k.startswith("list:")]),
        }
        
        # Get TTL info for some keys
        if all_keys:
            sample_key = all_keys[0]
            stats["sample_ttl"] = await self.ttl(sample_key)
        
        return stats
    
    # Bulk operations
    async def warm_category_cache(self, categories: List[Dict[str, Any]]) -> None:
        """Warm cache with category data"""
        cache_data = {}
        
        for category in categories:
            category_id = category.get("id")
            if category_id:
                key = f"cat:{category_id}"
                cache_data[key] = category
        
        if cache_data:
            await self.set_many(cache_data, ttl=self.ttl_category)
            logger.info(f"Warmed cache with {len(cache_data)} categories")
    
    async def preload_popular_categories(self, category_ids: List[UUID]) -> None:
        """Preload popular categories into cache"""
        # This would typically be called with data from the database
        # For now, we'll just ensure the keys exist in cache
        for category_id in category_ids:
            if not await self.exists(f"cat:{category_id}"):
                logger.info(f"Category {category_id} not in cache, should be loaded")
    
    # Search-related caching
    async def get_category_search_results(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Get category search results from cache"""
        filter_hash = self._hash_key(filters) if filters else "none"
        query_hash = self._hash_key(query)
        key = f"search:{query_hash}:{filter_hash}"
        return await self.get(key)
    
    async def set_category_search_results(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        results: List[Dict[str, Any]]
    ) -> bool:
        """Cache category search results"""
        filter_hash = self._hash_key(filters) if filters else "none"
        query_hash = self._hash_key(query)
        key = f"search:{query_hash}:{filter_hash}"
        # Shorter TTL for search results
        return await self.set(key, results, ttl=300)  # 5 minutes