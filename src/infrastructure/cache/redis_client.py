"""
Redis client configuration and connection management
"""

import json
import logging
from typing import Any, Optional, Union, Dict, List
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError

from ..config.settings import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client wrapper with connection management and error handling"""
    
    def __init__(self):
        self._client: Optional[Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
    
    async def connect(self) -> None:
        """Initialize Redis connection"""
        try:
            # Create connection pool
            self._connection_pool = redis.ConnectionPool(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                decode_responses=True,
                max_connections=settings.redis_max_connections,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30
            )
            
            # Create Redis client
            self._client = Redis(connection_pool=self._connection_pool)
            
            # Test connection
            await self._client.ping()
            logger.info("Redis connection established successfully")
            
        except ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            logger.info("Redis connection closed")
    
    @property
    def client(self) -> Redis:
        """Get Redis client instance"""
        if not self._client:
            raise RuntimeError("Redis client not initialized. Call connect() first.")
        return self._client
    
    async def is_connected(self) -> bool:
        """Check if Redis is connected and responsive"""
        try:
            if not self._client:
                return False
            await self._client.ping()
            return True
        except RedisError:
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        try:
            return await self.client.get(key)
        except RedisError as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        ex: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """Set key-value pair with optional expiration"""
        try:
            return await self.client.set(key, value, ex=ex, nx=nx)
        except RedisError as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        try:
            return await self.client.delete(*keys)
        except RedisError as e:
            logger.error(f"Redis DELETE error for keys {keys}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(await self.client.exists(key))
        except RedisError as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key"""
        try:
            return await self.client.expire(key, seconds)
        except RedisError as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key"""
        try:
            return await self.client.ttl(key)
        except RedisError as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -1
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern"""
        try:
            return await self.client.keys(pattern)
        except RedisError as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []
    
    async def flushdb(self) -> bool:
        """Clear current database"""
        try:
            await self.client.flushdb()
            return True
        except RedisError as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False
    
    # JSON operations
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and deserialize JSON value"""
        try:
            value = await self.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (json.JSONDecodeError, RedisError) as e:
            logger.error(f"Redis GET_JSON error for key {key}: {e}")
            return None
    
    async def set_json(
        self, 
        key: str, 
        value: Any, 
        ex: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """Serialize and set JSON value"""
        try:
            json_value = json.dumps(value, default=str)
            return await self.set(key, json_value, ex=ex, nx=nx)
        except (json.JSONEncodeError, RedisError) as e:
            logger.error(f"Redis SET_JSON error for key {key}: {e}")
            return False
    
    # Hash operations
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value"""
        try:
            return await self.client.hget(name, key)
        except RedisError as e:
            logger.error(f"Redis HGET error for {name}.{key}: {e}")
            return None
    
    async def hset(self, name: str, key: str, value: str) -> bool:
        """Set hash field value"""
        try:
            return bool(await self.client.hset(name, key, value))
        except RedisError as e:
            logger.error(f"Redis HSET error for {name}.{key}: {e}")
            return False
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Get all hash fields"""
        try:
            return await self.client.hgetall(name)
        except RedisError as e:
            logger.error(f"Redis HGETALL error for {name}: {e}")
            return {}
    
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields"""
        try:
            return await self.client.hdel(name, *keys)
        except RedisError as e:
            logger.error(f"Redis HDEL error for {name}: {e}")
            return 0
    
    # List operations
    async def lpush(self, name: str, *values: str) -> int:
        """Push values to list head"""
        try:
            return await self.client.lpush(name, *values)
        except RedisError as e:
            logger.error(f"Redis LPUSH error for {name}: {e}")
            return 0
    
    async def rpush(self, name: str, *values: str) -> int:
        """Push values to list tail"""
        try:
            return await self.client.rpush(name, *values)
        except RedisError as e:
            logger.error(f"Redis RPUSH error for {name}: {e}")
            return 0
    
    async def lrange(self, name: str, start: int, end: int) -> List[str]:
        """Get list range"""
        try:
            return await self.client.lrange(name, start, end)
        except RedisError as e:
            logger.error(f"Redis LRANGE error for {name}: {e}")
            return []
    
    async def ltrim(self, name: str, start: int, end: int) -> bool:
        """Trim list to range"""
        try:
            await self.client.ltrim(name, start, end)
            return True
        except RedisError as e:
            logger.error(f"Redis LTRIM error for {name}: {e}")
            return False


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis_client() -> RedisClient:
    """Get or create Redis client instance"""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = RedisClient()
        await _redis_client.connect()
    
    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client connection"""
    global _redis_client
    
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None


@asynccontextmanager
async def redis_client():
    """Context manager for Redis client"""
    client = await get_redis_client()
    try:
        yield client
    finally:
        # Connection is managed globally, don't close here
        pass