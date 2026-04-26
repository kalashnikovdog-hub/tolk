"""
Redis Cache Manager for caching popular requests
"""
import json
import logging
from typing import Any, Optional, List, Dict
from datetime import timedelta
import redis.asyncio as redis

from app.config.settings import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Async Redis cache manager"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = settings.CACHE_TTL
    
    def _make_key(self, prefix: str, identifier: Any) -> str:
        """Create cache key"""
        return f"{prefix}:{identifier}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if not self.redis:
                return None
            
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = None
    ) -> bool:
        """Set value in cache with TTL"""
        try:
            if not self.redis:
                return False
            
            ttl = ttl or self.default_ttl
            
            # Serialize to JSON if needed
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.redis.setex(key, ttl, value)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if not self.redis:
                return False
            
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> bool:
        """Delete all keys matching pattern"""
        try:
            if not self.redis:
                return False
            
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache delete_pattern error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if not self.redis:
                return False
            
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    # Convenience methods for common cache operations
    
    async def get_discount(self, discount_id: int) -> Optional[Dict]:
        """Get discounted item from cache"""
        key = self._make_key("discount", discount_id)
        return await self.get(key)
    
    async def set_discount(self, discount_id: int, data: Dict, ttl: int = None) -> bool:
        """Cache discounted item"""
        key = self._make_key("discount", discount_id)
        return await self.set(key, data, ttl)
    
    async def get_discounts_list(self, filters_hash: str) -> Optional[List[Dict]]:
        """Get list of discounts from cache"""
        key = self._make_key("discounts:list", filters_hash)
        return await self.get(key)
    
    async def set_discounts_list(
        self,
        filters_hash: str,
        data: List[Dict],
        ttl: int = None
    ) -> bool:
        """Cache list of discounts"""
        key = self._make_key("discounts:list", filters_hash)
        return await self.set(key, data, ttl)
    
    async def get_store(self, store_id: int) -> Optional[Dict]:
        """Get store from cache"""
        key = self._make_key("store", store_id)
        return await self.get(key)
    
    async def set_store(self, store_id: int, data: Dict, ttl: int = None) -> bool:
        """Cache store"""
        key = self._make_key("store", store_id)
        return await self.set(key, data, ttl)
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user from cache"""
        key = self._make_key("user", user_id)
        return await self.get(key)
    
    async def set_user(self, user_id: int, data: Dict, ttl: int = 3600) -> bool:
        """Cache user (longer TTL)"""
        key = self._make_key("user", user_id)
        return await self.set(key, data, ttl)
    
    async def invalidate_user_cache(self, user_id: int) -> bool:
        """Invalidate user cache"""
        key = self._make_key("user", user_id)
        return await self.delete(key)
    
    async def invalidate_discount_cache(self, discount_id: int) -> bool:
        """Invalidate discount cache"""
        key = self._make_key("discount", discount_id)
        return await self.delete(key)
    
    async def invalidate_discounts_list_cache(self) -> bool:
        """Invalidate all discounts list cache"""
        return await self.delete_pattern("discounts:list:*")
    
    async def cache_or_get(
        self,
        key: str,
        fetch_func,
        ttl: int = None
    ) -> Any:
        """
        Get from cache or fetch and cache
        
        Args:
            key: Cache key
            fetch_func: Async function to call if cache miss
            ttl: Time to live in seconds
        
        Returns:
            Cached or fetched value
        """
        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            logger.debug(f"Cache hit for key: {key}")
            return cached
        
        # Cache miss - fetch
        logger.debug(f"Cache miss for key: {key}, fetching...")
        value = await fetch_func()
        
        # Cache the result
        if value is not None:
            await self.set(key, value, ttl)
        
        return value
