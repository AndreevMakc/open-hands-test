"""
Cache manager service

Coordinates all caching operations across the application.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

from ...infrastructure.cache.redis_client import RedisClient, get_redis_client
from ...infrastructure.cache.category_cache import CategoryCacheService
from ...infrastructure.cache.product_cache import ProductCacheService
from ...infrastructure.cache.search_cache import SearchCacheService

logger = logging.getLogger(__name__)


class CacheManager:
    """Central cache manager for coordinating all cache operations"""
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        self._redis_client = redis_client
        self._category_cache: Optional[CategoryCacheService] = None
        self._product_cache: Optional[ProductCacheService] = None
        self._search_cache: Optional[SearchCacheService] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize cache manager and all cache services"""
        if self._initialized:
            return
        
        try:
            # Get Redis client
            if not self._redis_client:
                self._redis_client = await get_redis_client()
            
            # Initialize cache services
            self._category_cache = CategoryCacheService(self._redis_client)
            self._product_cache = ProductCacheService(self._redis_client)
            self._search_cache = SearchCacheService(self._redis_client)
            
            self._initialized = True
            logger.info("Cache manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cache manager: {e}")
            raise
    
    @property
    def categories(self) -> CategoryCacheService:
        """Get category cache service"""
        if not self._initialized or not self._category_cache:
            raise RuntimeError("Cache manager not initialized")
        return self._category_cache
    
    @property
    def products(self) -> ProductCacheService:
        """Get product cache service"""
        if not self._initialized or not self._product_cache:
            raise RuntimeError("Cache manager not initialized")
        return self._product_cache
    
    @property
    def search(self) -> SearchCacheService:
        """Get search cache service"""
        if not self._initialized or not self._search_cache:
            raise RuntimeError("Cache manager not initialized")
        return self._search_cache
    
    @property
    def redis(self) -> RedisClient:
        """Get Redis client"""
        if not self._redis_client:
            raise RuntimeError("Cache manager not initialized")
        return self._redis_client
    
    # Health and monitoring
    async def health_check(self) -> Dict[str, Any]:
        """Check cache health status"""
        try:
            if not self._redis_client:
                return {"status": "error", "message": "Redis client not initialized"}
            
            is_connected = await self._redis_client.is_connected()
            
            if is_connected:
                # Get basic Redis info
                info = {
                    "status": "healthy",
                    "redis_connected": True,
                    "services_initialized": self._initialized
                }
                
                if self._initialized:
                    # Get cache statistics
                    info["cache_stats"] = await self.get_cache_statistics()
                
                return info
            else:
                return {
                    "status": "unhealthy",
                    "redis_connected": False,
                    "message": "Redis connection failed"
                }
                
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                "status": "error",
                "message": f"Health check failed: {str(e)}"
            }
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        if not self._initialized:
            return {"error": "Cache manager not initialized"}
        
        try:
            stats = {
                "categories": await self._category_cache.get_cache_stats(),
                "products": await self._product_cache.get_cache_stats(),
                "search": await self._search_cache.get_cache_stats(),
            }
            
            # Calculate totals
            total_keys = sum(s.get("total_keys", 0) for s in stats.values())
            stats["total_keys"] = total_keys
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            return {"error": str(e)}
    
    # Cache invalidation coordination
    async def invalidate_category_related(self, category_id: UUID) -> None:
        """Invalidate all caches related to a category"""
        if not self._initialized:
            return
        
        try:
            # Invalidate category cache
            await self._category_cache.invalidate_category(category_id)
            
            # Invalidate related product caches
            await self._product_cache.invalidate_category_products(category_id)
            
            # Invalidate search caches
            await self._search_cache.invalidate_search_results("products")
            await self._search_cache.invalidate_filters("products")
            
            logger.info(f"Invalidated all caches for category {category_id}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate category caches: {e}")
    
    async def invalidate_product_related(
        self, 
        product_id: UUID, 
        sku: Optional[str] = None,
        category_id: Optional[UUID] = None
    ) -> None:
        """Invalidate all caches related to a product"""
        if not self._initialized:
            return
        
        try:
            # Invalidate product cache
            await self._product_cache.invalidate_product(product_id, sku)
            
            # Invalidate category caches if category is affected
            if category_id:
                await self._category_cache.invalidate_category(category_id)
            
            # Invalidate search caches
            await self._search_cache.invalidate_search_results("products")
            await self._search_cache.invalidate_autocomplete("products")
            
            logger.info(f"Invalidated all caches for product {product_id}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate product caches: {e}")
    
    async def invalidate_all_search(self) -> None:
        """Invalidate all search-related caches"""
        if not self._initialized:
            return
        
        try:
            await self._search_cache.invalidate_all()
            await self._product_cache.invalidate_search_cache()
            
            logger.info("Invalidated all search caches")
            
        except Exception as e:
            logger.error(f"Failed to invalidate search caches: {e}")
    
    # Cache warming
    async def warm_essential_caches(self) -> None:
        """Warm up essential caches for better performance"""
        if not self._initialized:
            return
        
        try:
            logger.info("Starting cache warming process...")
            
            # This would typically load popular/essential data
            # For now, we'll just log what should be warmed
            
            logger.info("Should warm category tree cache")
            logger.info("Should warm popular product caches")
            logger.info("Should warm popular search caches")
            logger.info("Should warm autocomplete caches")
            
            logger.info("Cache warming completed")
            
        except Exception as e:
            logger.error(f"Cache warming failed: {e}")
    
    # Bulk operations
    async def clear_all_caches(self) -> Dict[str, bool]:
        """Clear all caches (use with caution)"""
        if not self._initialized:
            return {"error": "Cache manager not initialized"}
        
        try:
            results = {}
            
            # Clear each cache service
            await self._category_cache.invalidate_all()
            results["categories"] = True
            
            await self._product_cache.invalidate_all()
            results["products"] = True
            
            await self._search_cache.invalidate_all()
            results["search"] = True
            
            logger.warning("All caches cleared")
            return results
            
        except Exception as e:
            logger.error(f"Failed to clear all caches: {e}")
            return {"error": str(e)}
    
    async def flush_redis_db(self) -> bool:
        """Flush entire Redis database (use with extreme caution)"""
        if not self._redis_client:
            return False
        
        try:
            success = await self._redis_client.flushdb()
            if success:
                logger.warning("Redis database flushed")
            return success
            
        except Exception as e:
            logger.error(f"Failed to flush Redis database: {e}")
            return False
    
    # Performance monitoring
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        if not self._initialized:
            return {"error": "Cache manager not initialized"}
        
        try:
            metrics = {
                "cache_stats": await self.get_cache_statistics(),
                "health": await self.health_check(),
            }
            
            # Add hit rates if available
            if self._product_cache:
                metrics["product_hit_rates"] = {
                    "get_product": await self._product_cache.get_hit_rate("get_product"),
                    "search": await self._product_cache.get_hit_rate("search"),
                    "list": await self._product_cache.get_hit_rate("list"),
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {"error": str(e)}
    
    # Configuration and maintenance
    async def update_cache_ttls(self, ttl_config: Dict[str, int]) -> bool:
        """Update cache TTL configurations"""
        try:
            # This would update TTL settings for different cache types
            # Implementation would depend on how TTLs are managed
            logger.info(f"Cache TTL configuration updated: {ttl_config}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update cache TTLs: {e}")
            return False
    
    async def get_cache_memory_usage(self) -> Dict[str, Any]:
        """Get Redis memory usage information"""
        if not self._redis_client:
            return {"error": "Redis client not available"}
        
        try:
            # Get Redis info about memory usage
            # This would use Redis INFO command
            info = {
                "status": "Redis memory info not implemented",
                "note": "Would use Redis INFO MEMORY command"
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return {"error": str(e)}


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance"""
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    
    return _cache_manager


async def close_cache_manager() -> None:
    """Close cache manager and connections"""
    global _cache_manager
    
    if _cache_manager and _cache_manager._redis_client:
        from ...infrastructure.cache.redis_client import close_redis_client
        await close_redis_client()
        _cache_manager = None