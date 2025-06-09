"""
Generic cache service with common caching patterns
"""

import hashlib
import logging
from typing import Any, Optional, Dict, List, Callable, TypeVar, Union
from functools import wraps

from .redis_client import RedisClient

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CacheService:
    """Generic cache service with common caching operations"""
    
    def __init__(self, redis_client: RedisClient, key_prefix: str = ""):
        self.redis = redis_client
        self.key_prefix = key_prefix
    
    def _make_key(self, key: str) -> str:
        """Create cache key with prefix"""
        if self.key_prefix:
            return f"{self.key_prefix}:{key}"
        return key
    
    def _hash_key(self, data: Any) -> str:
        """Create hash from data for cache key"""
        if isinstance(data, dict):
            # Sort dict for consistent hashing
            sorted_items = sorted(data.items())
            data_str = str(sorted_items)
        else:
            data_str = str(data)
        
        return hashlib.md5(data_str.encode()).hexdigest()[:16]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._make_key(key)
        return await self.redis.get_json(cache_key)
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """Set value in cache"""
        cache_key = self._make_key(key)
        return await self.redis.set_json(cache_key, value, ex=ttl, nx=nx)
    
    async def delete(self, *keys: str) -> int:
        """Delete keys from cache"""
        cache_keys = [self._make_key(key) for key in keys]
        return await self.redis.delete(*cache_keys)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        cache_key = self._make_key(key)
        return await self.redis.exists(cache_key)
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key"""
        cache_key = self._make_key(key)
        return await self.redis.expire(cache_key, ttl)
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key"""
        cache_key = self._make_key(key)
        return await self.redis.ttl(cache_key)
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        cache_pattern = self._make_key(pattern)
        keys = await self.redis.keys(cache_pattern)
        
        # Remove prefix from returned keys
        if self.key_prefix:
            prefix_len = len(self.key_prefix) + 1  # +1 for ':'
            return [key[prefix_len:] for key in keys if key.startswith(self.key_prefix)]
        
        return keys
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        keys = await self.keys(pattern)
        if keys:
            return await self.delete(*keys)
        return 0
    
    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """Get value from cache or set it using factory function"""
        value = await self.get(key)
        
        if value is not None:
            return value
        
        # Generate value using factory
        try:
            if callable(factory):
                value = await factory() if hasattr(factory, '__await__') else factory()
            else:
                value = factory
            
            # Cache the value
            await self.set(key, value, ttl=ttl)
            return value
            
        except Exception as e:
            logger.error(f"Error in cache factory for key {key}: {e}")
            raise
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache"""
        result = {}
        
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        
        return result
    
    async def set_many(
        self, 
        data: Dict[str, Any], 
        ttl: Optional[int] = None
    ) -> Dict[str, bool]:
        """Set multiple values in cache"""
        result = {}
        
        for key, value in data.items():
            result[key] = await self.set(key, value, ttl=ttl)
        
        return result
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in cache"""
        cache_key = self._make_key(key)
        try:
            return await self.redis.client.incr(cache_key, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {key}: {e}")
            return 0
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value in cache"""
        cache_key = self._make_key(key)
        try:
            return await self.redis.client.decr(cache_key, amount)
        except Exception as e:
            logger.error(f"Error decrementing key {key}: {e}")
            return 0
    
    # List operations
    async def list_push(self, key: str, *values: Any) -> int:
        """Push values to list"""
        cache_key = self._make_key(key)
        json_values = [str(v) for v in values]
        return await self.redis.lpush(cache_key, *json_values)
    
    async def list_pop(self, key: str) -> Optional[Any]:
        """Pop value from list"""
        cache_key = self._make_key(key)
        try:
            value = await self.redis.client.lpop(cache_key)
            return value
        except Exception as e:
            logger.error(f"Error popping from list {key}: {e}")
            return None
    
    async def list_range(self, key: str, start: int = 0, end: int = -1) -> List[Any]:
        """Get range from list"""
        cache_key = self._make_key(key)
        return await self.redis.lrange(cache_key, start, end)
    
    async def list_trim(self, key: str, start: int, end: int) -> bool:
        """Trim list to range"""
        cache_key = self._make_key(key)
        return await self.redis.ltrim(cache_key, start, end)
    
    # Hash operations
    async def hash_get(self, name: str, key: str) -> Optional[Any]:
        """Get hash field value"""
        cache_name = self._make_key(name)
        value = await self.redis.hget(cache_name, key)
        if value:
            try:
                import json
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def hash_set(self, name: str, key: str, value: Any) -> bool:
        """Set hash field value"""
        cache_name = self._make_key(name)
        import json
        json_value = json.dumps(value, default=str)
        return await self.redis.hset(cache_name, key, json_value)
    
    async def hash_get_all(self, name: str) -> Dict[str, Any]:
        """Get all hash fields"""
        cache_name = self._make_key(name)
        hash_data = await self.redis.hgetall(cache_name)
        
        result = {}
        for key, value in hash_data.items():
            try:
                import json
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                result[key] = value
        
        return result
    
    async def hash_delete(self, name: str, *keys: str) -> int:
        """Delete hash fields"""
        cache_name = self._make_key(name)
        return await self.redis.hdel(cache_name, *keys)


def cache_result(
    key_template: str,
    ttl: Optional[int] = None,
    cache_service: Optional[CacheService] = None
):
    """Decorator to cache function results"""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if cache_service is None:
                # If no cache service provided, just call the function
                return await func(*args, **kwargs)
            
            # Generate cache key from template and arguments
            try:
                cache_key = key_template.format(*args, **kwargs)
            except (KeyError, IndexError):
                # If key template doesn't match arguments, generate hash
                cache_key = f"{func.__name__}:{cache_service._hash_key((args, kwargs))}"
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator