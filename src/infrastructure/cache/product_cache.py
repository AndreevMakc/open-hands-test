"""
Product-specific caching service
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from .cache_service import CacheService
from .redis_client import RedisClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ProductCacheService(CacheService):
    """Cache service for product operations"""
    
    def __init__(self, redis_client: RedisClient):
        super().__init__(redis_client, key_prefix="product")
        self.ttl_product = settings.cache_ttl_product_details
        self.ttl_list = 600  # 10 minutes for product lists
        self.ttl_search = settings.cache_ttl_search_results
        self.ttl_stats = 300  # 5 minutes for statistics
    
    # Product caching
    async def get_product(self, product_id: UUID) -> Optional[Dict[str, Any]]:
        """Get product from cache"""
        key = f"prod:{product_id}"
        return await self.get(key)
    
    async def set_product(self, product_id: UUID, product_data: Dict[str, Any]) -> bool:
        """Cache product data"""
        key = f"prod:{product_id}"
        return await self.set(key, product_data, ttl=self.ttl_product)
    
    async def delete_product(self, product_id: UUID) -> int:
        """Remove product from cache"""
        key = f"prod:{product_id}"
        return await self.delete(key)
    
    # Product by SKU caching
    async def get_product_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get product by SKU from cache"""
        key = f"sku:{sku}"
        return await self.get(key)
    
    async def set_product_by_sku(self, sku: str, product_data: Dict[str, Any]) -> bool:
        """Cache product by SKU"""
        key = f"sku:{sku}"
        return await self.set(key, product_data, ttl=self.ttl_product)
    
    async def delete_product_by_sku(self, sku: str) -> int:
        """Remove product by SKU from cache"""
        key = f"sku:{sku}"
        return await self.delete(key)
    
    # Product list caching
    async def get_product_list(
        self,
        page: int = 1,
        size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Optional[Dict[str, Any]]:
        """Get product list from cache"""
        filter_hash = self._hash_key(filters) if filters else "all"
        key = f"list:{page}:{size}:{sort_by}:{sort_order}:{filter_hash}"
        return await self.get(key)
    
    async def set_product_list(
        self,
        page: int,
        size: int,
        filters: Optional[Dict[str, Any]],
        sort_by: str,
        sort_order: str,
        list_data: Dict[str, Any]
    ) -> bool:
        """Cache product list"""
        filter_hash = self._hash_key(filters) if filters else "all"
        key = f"list:{page}:{size}:{sort_by}:{sort_order}:{filter_hash}"
        return await self.set(key, list_data, ttl=self.ttl_list)
    
    # Products by category caching
    async def get_products_by_category(
        self,
        category_id: UUID,
        include_subcategories: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """Get products by category from cache"""
        key = f"cat:{category_id}:subs:{include_subcategories}"
        return await self.get(key)
    
    async def set_products_by_category(
        self,
        category_id: UUID,
        include_subcategories: bool,
        products_data: List[Dict[str, Any]]
    ) -> bool:
        """Cache products by category"""
        key = f"cat:{category_id}:subs:{include_subcategories}"
        return await self.set(key, products_data, ttl=self.ttl_list)
    
    async def delete_products_by_category(self, category_id: UUID) -> int:
        """Remove products by category from cache"""
        # Delete both with and without subcategories
        keys = [
            f"cat:{category_id}:subs:True",
            f"cat:{category_id}:subs:False"
        ]
        return await self.delete(*keys)
    
    # Product search caching
    async def get_search_results(
        self,
        query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20,
        sort_by: str = "relevance",
        sort_order: str = "desc"
    ) -> Optional[Dict[str, Any]]:
        """Get search results from cache"""
        search_params = {
            "query": query,
            "filters": filters,
            "page": page,
            "size": size,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        search_hash = self._hash_key(search_params)
        key = f"search:{search_hash}"
        return await self.get(key)
    
    async def set_search_results(
        self,
        query: Optional[str],
        filters: Optional[Dict[str, Any]],
        page: int,
        size: int,
        sort_by: str,
        sort_order: str,
        results: Dict[str, Any]
    ) -> bool:
        """Cache search results"""
        search_params = {
            "query": query,
            "filters": filters,
            "page": page,
            "size": size,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        search_hash = self._hash_key(search_params)
        key = f"search:{search_hash}"
        return await self.set(key, results, ttl=self.ttl_search)
    
    # Product statistics caching
    async def get_product_stats(self) -> Optional[Dict[str, Any]]:
        """Get product statistics from cache"""
        return await self.get("stats:overview")
    
    async def set_product_stats(self, stats_data: Dict[str, Any]) -> bool:
        """Cache product statistics"""
        return await self.set("stats:overview", stats_data, ttl=self.ttl_stats)
    
    async def delete_product_stats(self) -> int:
        """Remove product statistics from cache"""
        return await self.delete("stats:overview")
    
    # Featured products caching
    async def get_featured_products(self, limit: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        """Get featured products from cache"""
        key = f"featured:{limit or 'all'}"
        return await self.get(key)
    
    async def set_featured_products(
        self,
        limit: Optional[int],
        products_data: List[Dict[str, Any]]
    ) -> bool:
        """Cache featured products"""
        key = f"featured:{limit or 'all'}"
        return await self.set(key, products_data, ttl=self.ttl_list)
    
    async def delete_featured_products(self) -> int:
        """Remove featured products from cache"""
        return await self.clear_pattern("featured:*")
    
    # Cache invalidation methods
    async def invalidate_product(self, product_id: UUID, sku: Optional[str] = None) -> None:
        """Invalidate all cache entries for a product"""
        await self.delete_product(product_id)
        
        if sku:
            await self.delete_product_by_sku(sku)
        
        # Clear related caches
        await self.clear_pattern("list:*")
        await self.clear_pattern("search:*")
        await self.clear_pattern("cat:*")
        await self.delete_featured_products()
        await self.delete_product_stats()
        
        logger.info(f"Invalidated cache for product {product_id}")
    
    async def invalidate_category_products(self, category_id: UUID) -> None:
        """Invalidate product caches for a category"""
        await self.delete_products_by_category(category_id)
        await self.clear_pattern("list:*")
        await self.clear_pattern("search:*")
        
        logger.info(f"Invalidated product cache for category {category_id}")
    
    async def invalidate_search_cache(self) -> None:
        """Invalidate all search caches"""
        await self.clear_pattern("search:*")
        logger.info("Invalidated product search cache")
    
    async def invalidate_all(self) -> None:
        """Invalidate all product caches"""
        await self.clear_pattern("*")
        logger.info("Invalidated all product caches")
    
    # Bulk operations
    async def warm_product_cache(self, products: List[Dict[str, Any]]) -> None:
        """Warm cache with product data"""
        cache_data = {}
        
        for product in products:
            product_id = product.get("id")
            sku = product.get("sku")
            
            if product_id:
                cache_data[f"prod:{product_id}"] = product
            
            if sku:
                cache_data[f"sku:{sku}"] = product
        
        if cache_data:
            await self.set_many(cache_data, ttl=self.ttl_product)
            logger.info(f"Warmed cache with {len(products)} products")
    
    async def preload_popular_products(self, product_ids: List[UUID]) -> None:
        """Preload popular products into cache"""
        for product_id in product_ids:
            if not await self.exists(f"prod:{product_id}"):
                logger.info(f"Product {product_id} not in cache, should be loaded")
    
    # Advanced search caching
    async def get_autocomplete_suggestions(self, query: str) -> Optional[List[str]]:
        """Get autocomplete suggestions from cache"""
        query_hash = self._hash_key(query.lower())
        key = f"autocomplete:{query_hash}"
        return await self.get(key)
    
    async def set_autocomplete_suggestions(
        self,
        query: str,
        suggestions: List[str]
    ) -> bool:
        """Cache autocomplete suggestions"""
        query_hash = self._hash_key(query.lower())
        key = f"autocomplete:{query_hash}"
        return await self.set(key, suggestions, ttl=3600)  # 1 hour
    
    # Product filters caching
    async def get_available_filters(self, category_id: Optional[UUID] = None) -> Optional[Dict[str, Any]]:
        """Get available filters from cache"""
        key = f"filters:{category_id or 'all'}"
        return await self.get(key)
    
    async def set_available_filters(
        self,
        category_id: Optional[UUID],
        filters_data: Dict[str, Any]
    ) -> bool:
        """Cache available filters"""
        key = f"filters:{category_id or 'all'}"
        return await self.set(key, filters_data, ttl=1800)  # 30 minutes
    
    # Statistics and monitoring
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for products"""
        all_keys = await self.keys("*")
        
        stats = {
            "total_keys": len(all_keys),
            "products": len([k for k in all_keys if k.startswith("prod:")]),
            "skus": len([k for k in all_keys if k.startswith("sku:")]),
            "lists": len([k for k in all_keys if k.startswith("list:")]),
            "searches": len([k for k in all_keys if k.startswith("search:")]),
            "categories": len([k for k in all_keys if k.startswith("cat:")]),
            "featured": len([k for k in all_keys if k.startswith("featured:")]),
            "stats": len([k for k in all_keys if k.startswith("stats:")]),
            "autocomplete": len([k for k in all_keys if k.startswith("autocomplete:")]),
            "filters": len([k for k in all_keys if k.startswith("filters:")]),
        }
        
        # Get TTL info for some keys
        if all_keys:
            sample_key = all_keys[0]
            stats["sample_ttl"] = await self.ttl(sample_key)
        
        return stats
    
    # Cache warming strategies
    async def warm_popular_searches(self, popular_queries: List[str]) -> None:
        """Warm cache with popular search queries"""
        # This would typically execute the searches to populate cache
        for query in popular_queries:
            logger.info(f"Should warm cache for popular query: {query}")
    
    async def warm_category_products(self, category_ids: List[UUID]) -> None:
        """Warm cache with products from popular categories"""
        for category_id in category_ids:
            logger.info(f"Should warm cache for category: {category_id}")
    
    # Performance monitoring
    async def track_cache_hit(self, operation: str) -> None:
        """Track cache hit for monitoring"""
        await self.increment(f"metrics:hits:{operation}")
    
    async def track_cache_miss(self, operation: str) -> None:
        """Track cache miss for monitoring"""
        await self.increment(f"metrics:misses:{operation}")
    
    async def get_hit_rate(self, operation: str) -> float:
        """Get cache hit rate for operation"""
        hits = await self.get(f"metrics:hits:{operation}") or 0
        misses = await self.get(f"metrics:misses:{operation}") or 0
        
        total = hits + misses
        if total == 0:
            return 0.0
        
        return hits / total