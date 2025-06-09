"""
Search-specific caching service
"""

import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from .cache_service import CacheService
from .redis_client import RedisClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


class SearchCacheService(CacheService):
    """Cache service for search operations"""
    
    def __init__(self, redis_client: RedisClient):
        super().__init__(redis_client, key_prefix="search")
        self.ttl_search = settings.cache_ttl_search_results
        self.ttl_autocomplete = 3600  # 1 hour for autocomplete
        self.ttl_suggestions = 1800   # 30 minutes for suggestions
        self.ttl_filters = 1800       # 30 minutes for filter options
    
    # Search results caching
    async def get_search_results(
        self,
        entity_type: str,  # 'products', 'categories', 'attributes'
        search_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get search results from cache"""
        params_hash = self._hash_key(search_params)
        key = f"{entity_type}:results:{params_hash}"
        return await self.get(key)
    
    async def set_search_results(
        self,
        entity_type: str,
        search_params: Dict[str, Any],
        results: Dict[str, Any]
    ) -> bool:
        """Cache search results"""
        params_hash = self._hash_key(search_params)
        key = f"{entity_type}:results:{params_hash}"
        return await self.set(key, results, ttl=self.ttl_search)
    
    # Autocomplete caching
    async def get_autocomplete(
        self,
        entity_type: str,
        query: str,
        limit: int = 10
    ) -> Optional[List[str]]:
        """Get autocomplete suggestions from cache"""
        query_normalized = query.lower().strip()
        query_hash = self._hash_key(f"{query_normalized}:{limit}")
        key = f"{entity_type}:autocomplete:{query_hash}"
        return await self.get(key)
    
    async def set_autocomplete(
        self,
        entity_type: str,
        query: str,
        limit: int,
        suggestions: List[str]
    ) -> bool:
        """Cache autocomplete suggestions"""
        query_normalized = query.lower().strip()
        query_hash = self._hash_key(f"{query_normalized}:{limit}")
        key = f"{entity_type}:autocomplete:{query_hash}"
        return await self.set(key, suggestions, ttl=self.ttl_autocomplete)
    
    # Search suggestions caching
    async def get_search_suggestions(
        self,
        entity_type: str,
        query: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Get search suggestions from cache"""
        query_normalized = query.lower().strip()
        query_hash = self._hash_key(query_normalized)
        key = f"{entity_type}:suggestions:{query_hash}"
        return await self.get(key)
    
    async def set_search_suggestions(
        self,
        entity_type: str,
        query: str,
        suggestions: List[Dict[str, Any]]
    ) -> bool:
        """Cache search suggestions"""
        query_normalized = query.lower().strip()
        query_hash = self._hash_key(query_normalized)
        key = f"{entity_type}:suggestions:{query_hash}"
        return await self.set(key, suggestions, ttl=self.ttl_suggestions)
    
    # Popular searches caching
    async def get_popular_searches(
        self,
        entity_type: str,
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """Get popular searches from cache"""
        key = f"{entity_type}:popular:{limit}"
        return await self.get(key)
    
    async def set_popular_searches(
        self,
        entity_type: str,
        limit: int,
        searches: List[Dict[str, Any]]
    ) -> bool:
        """Cache popular searches"""
        key = f"{entity_type}:popular:{limit}"
        return await self.set(key, searches, ttl=self.ttl_suggestions)
    
    # Search filters caching
    async def get_search_filters(
        self,
        entity_type: str,
        category_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Get available search filters from cache"""
        category_key = str(category_id) if category_id else "all"
        key = f"{entity_type}:filters:{category_key}"
        return await self.get(key)
    
    async def set_search_filters(
        self,
        entity_type: str,
        category_id: Optional[UUID],
        filters: Dict[str, Any]
    ) -> bool:
        """Cache search filters"""
        category_key = str(category_id) if category_id else "all"
        key = f"{entity_type}:filters:{category_key}"
        return await self.set(key, filters, ttl=self.ttl_filters)
    
    # Search facets caching
    async def get_search_facets(
        self,
        entity_type: str,
        search_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Get search facets from cache"""
        params_hash = self._hash_key(search_params)
        key = f"{entity_type}:facets:{params_hash}"
        return await self.get(key)
    
    async def set_search_facets(
        self,
        entity_type: str,
        search_params: Dict[str, Any],
        facets: Dict[str, Any]
    ) -> bool:
        """Cache search facets"""
        params_hash = self._hash_key(search_params)
        key = f"{entity_type}:facets:{params_hash}"
        return await self.set(key, facets, ttl=self.ttl_search)
    
    # Search analytics caching
    async def track_search_query(self, entity_type: str, query: str) -> None:
        """Track search query for analytics"""
        query_normalized = query.lower().strip()
        if not query_normalized:
            return
        
        # Increment search count
        key = f"{entity_type}:analytics:queries"
        await self.hash_set(key, query_normalized, 
                           await self.hash_get(key, query_normalized) or 0 + 1)
        
        # Add to recent searches
        recent_key = f"{entity_type}:analytics:recent"
        await self.list_push(recent_key, query_normalized)
        await self.list_trim(recent_key, 0, 999)  # Keep last 1000 searches
    
    async def get_search_analytics(
        self,
        entity_type: str,
        period: str = "day"
    ) -> Optional[Dict[str, Any]]:
        """Get search analytics from cache"""
        key = f"{entity_type}:analytics:{period}"
        return await self.get(key)
    
    async def set_search_analytics(
        self,
        entity_type: str,
        period: str,
        analytics: Dict[str, Any]
    ) -> bool:
        """Cache search analytics"""
        key = f"{entity_type}:analytics:{period}"
        ttl = 3600 if period == "hour" else 86400  # 1 hour or 1 day
        return await self.set(key, analytics, ttl=ttl)
    
    # Search performance caching
    async def get_search_performance(
        self,
        entity_type: str,
        query_hash: str
    ) -> Optional[Dict[str, Any]]:
        """Get search performance metrics from cache"""
        key = f"{entity_type}:performance:{query_hash}"
        return await self.get(key)
    
    async def set_search_performance(
        self,
        entity_type: str,
        query_hash: str,
        performance: Dict[str, Any]
    ) -> bool:
        """Cache search performance metrics"""
        key = f"{entity_type}:performance:{query_hash}"
        return await self.set(key, performance, ttl=3600)  # 1 hour
    
    # Cache invalidation methods
    async def invalidate_search_results(self, entity_type: str) -> None:
        """Invalidate search results for entity type"""
        await self.clear_pattern(f"{entity_type}:results:*")
        await self.clear_pattern(f"{entity_type}:facets:*")
        logger.info(f"Invalidated search results cache for {entity_type}")
    
    async def invalidate_autocomplete(self, entity_type: str) -> None:
        """Invalidate autocomplete cache for entity type"""
        await self.clear_pattern(f"{entity_type}:autocomplete:*")
        await self.clear_pattern(f"{entity_type}:suggestions:*")
        logger.info(f"Invalidated autocomplete cache for {entity_type}")
    
    async def invalidate_filters(self, entity_type: str) -> None:
        """Invalidate filters cache for entity type"""
        await self.clear_pattern(f"{entity_type}:filters:*")
        logger.info(f"Invalidated filters cache for {entity_type}")
    
    async def invalidate_all(self, entity_type: Optional[str] = None) -> None:
        """Invalidate all search caches"""
        if entity_type:
            await self.clear_pattern(f"{entity_type}:*")
            logger.info(f"Invalidated all search cache for {entity_type}")
        else:
            await self.clear_pattern("*")
            logger.info("Invalidated all search caches")
    
    # Bulk operations
    async def warm_popular_searches(
        self,
        entity_type: str,
        popular_queries: List[str]
    ) -> None:
        """Warm cache with popular search queries"""
        for query in popular_queries:
            # This would typically execute the search to populate cache
            logger.info(f"Should warm search cache for {entity_type}: {query}")
    
    async def warm_autocomplete(
        self,
        entity_type: str,
        common_prefixes: List[str]
    ) -> None:
        """Warm autocomplete cache with common prefixes"""
        for prefix in common_prefixes:
            # This would typically generate autocomplete suggestions
            logger.info(f"Should warm autocomplete cache for {entity_type}: {prefix}")
    
    # Statistics and monitoring
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for search"""
        all_keys = await self.keys("*")
        
        stats = {
            "total_keys": len(all_keys),
            "results": len([k for k in all_keys if ":results:" in k]),
            "autocomplete": len([k for k in all_keys if ":autocomplete:" in k]),
            "suggestions": len([k for k in all_keys if ":suggestions:" in k]),
            "filters": len([k for k in all_keys if ":filters:" in k]),
            "facets": len([k for k in all_keys if ":facets:" in k]),
            "analytics": len([k for k in all_keys if ":analytics:" in k]),
            "performance": len([k for k in all_keys if ":performance:" in k]),
            "popular": len([k for k in all_keys if ":popular:" in k]),
        }
        
        # Get entity type breakdown
        entity_types = set()
        for key in all_keys:
            if ":" in key:
                entity_type = key.split(":")[0]
                entity_types.add(entity_type)
        
        stats["entity_types"] = list(entity_types)
        
        return stats
    
    # Advanced search features
    async def get_search_history(
        self,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """Get search history from cache"""
        key = f"history:{user_id or 'anonymous'}:{limit}"
        return await self.get(key)
    
    async def add_to_search_history(
        self,
        query: str,
        entity_type: str,
        user_id: Optional[str] = None,
        results_count: int = 0
    ) -> bool:
        """Add search to history"""
        history_item = {
            "query": query,
            "entity_type": entity_type,
            "timestamp": "now",  # Would use actual timestamp
            "results_count": results_count
        }
        
        key = f"history:{user_id or 'anonymous'}"
        await self.list_push(key, str(history_item))
        await self.list_trim(key, 0, 99)  # Keep last 100 searches
        return True
    
    async def get_trending_searches(
        self,
        entity_type: str,
        period: str = "day",
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """Get trending searches from cache"""
        key = f"{entity_type}:trending:{period}:{limit}"
        return await self.get(key)
    
    async def set_trending_searches(
        self,
        entity_type: str,
        period: str,
        limit: int,
        trending: List[Dict[str, Any]]
    ) -> bool:
        """Cache trending searches"""
        key = f"{entity_type}:trending:{period}:{limit}"
        ttl = 3600 if period == "hour" else 86400  # 1 hour or 1 day
        return await self.set(key, trending, ttl=ttl)