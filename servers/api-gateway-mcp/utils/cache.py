"""
Cache utilities for API Gateway MCP Server
Provides response caching with TTL and memory management.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass, field
import logging

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False
    diskcache = None


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    data: Any
    timestamp: datetime
    ttl_seconds: int
    hit_count: int = 0
    provider: str = ""
    cost_saved: float = 0.0
    
    @property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)
    
    @property
    def age_seconds(self) -> int:
        """Get age of cache entry in seconds."""
        return int((datetime.now() - self.timestamp).total_seconds())


class BaseCache:
    """Base cache interface."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"api-gateway.cache.{name}")
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError
        
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        raise NotImplementedError
        
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        raise NotImplementedError
        
    async def clear(self) -> int:
        """Clear all cache entries."""
        raise NotImplementedError
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        raise NotImplementedError


class MemoryCache(BaseCache):
    """In-memory cache with TTL support."""
    
    def __init__(self, name: str = "memory", max_size: int = 1000):
        super().__init__(name)
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        entry = self.cache.get(key)
        
        if entry is None:
            self.misses += 1
            return None
            
        if entry.is_expired:
            # Remove expired entry
            del self.cache[key]
            self.misses += 1
            return None
            
        # Update hit count and stats
        entry.hit_count += 1
        self.hits += 1
        
        return entry.data
        
    async def set(self, key: str, value: Any, ttl: int = 3600, provider: str = "", cost_saved: float = 0.0) -> bool:
        """Set value in cache with TTL."""
        try:
            # Evict if at max size
            if len(self.cache) >= self.max_size:
                await self._evict_lru()
                
            entry = CacheEntry(
                data=value,
                timestamp=datetime.now(),
                ttl_seconds=ttl,
                provider=provider,
                cost_saved=cost_saved
            )
            
            self.cache[key] = entry
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set cache entry: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
        
    async def clear(self) -> int:
        """Clear all cache entries."""
        count = len(self.cache)
        self.cache.clear()
        return count
        
    async def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.cache:
            return
            
        # Find LRU entry (lowest hit_count, then oldest)
        lru_key = min(
            self.cache.keys(),
            key=lambda k: (self.cache[k].hit_count, self.cache[k].timestamp)
        )
        
        del self.cache[lru_key]
        self.evictions += 1
        
    async def _cleanup_loop(self):
        """Periodically clean up expired entries."""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                
                expired_keys = [
                    key for key, entry in self.cache.items()
                    if entry.is_expired
                ]
                
                for key in expired_keys:
                    del self.cache[key]
                    
                if expired_keys:
                    self.logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cache cleanup error: {e}")
                
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / max(1, total_requests)) * 100
        
        # Calculate total cost saved
        total_cost_saved = sum(entry.cost_saved for entry in self.cache.values())
        
        # Calculate size metrics
        active_entries = len([e for e in self.cache.values() if not e.is_expired])
        expired_entries = len(self.cache) - active_entries
        
        return {
            "type": "memory",
            "size": len(self.cache),
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
            "evictions": self.evictions,
            "total_cost_saved_usd": round(total_cost_saved, 4),
            "memory_usage_estimate_mb": len(self.cache) * 0.001  # Rough estimate
        }


class RedisCache(BaseCache):
    """Redis-based cache for production use."""
    
    def __init__(self, name: str = "redis", redis_url: str = "redis://localhost:6379", 
                 prefix: str = "api-gateway:"):
        super().__init__(name)
        self.redis_url = redis_url
        self.prefix = prefix
        self.redis_client = None
        self.hits = 0
        self.misses = 0
        
        if not REDIS_AVAILABLE:
            self.logger.error("Redis not available - install redis package")
            return
            
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            self.logger.info("Connected to Redis successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        if not self.redis_client:
            return None
            
        try:
            redis_key = f"{self.prefix}{key}"
            data = await self.redis_client.get(redis_key)
            
            if data is None:
                self.misses += 1
                return None
                
            # Deserialize data
            entry_data = json.loads(data)
            self.hits += 1
            
            return entry_data
            
        except Exception as e:
            self.logger.error(f"Redis get error: {e}")
            self.misses += 1
            return None
            
    async def set(self, key: str, value: Any, ttl: int = 3600, **kwargs) -> bool:
        """Set value in Redis cache with TTL."""
        if not self.redis_client:
            return False
            
        try:
            redis_key = f"{self.prefix}{key}"
            data = json.dumps(value, default=str)
            
            await self.redis_client.setex(redis_key, ttl, data)
            return True
            
        except Exception as e:
            self.logger.error(f"Redis set error: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from Redis cache."""
        if not self.redis_client:
            return False
            
        try:
            redis_key = f"{self.prefix}{key}"
            result = await self.redis_client.delete(redis_key)
            return result > 0
            
        except Exception as e:
            self.logger.error(f"Redis delete error: {e}")
            return False
            
    async def clear(self) -> int:
        """Clear all cache entries with our prefix."""
        if not self.redis_client:
            return 0
            
        try:
            pattern = f"{self.prefix}*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                result = await self.redis_client.delete(*keys)
                return result
            return 0
            
        except Exception as e:
            self.logger.error(f"Redis clear error: {e}")
            return 0
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        if not self.redis_client:
            return {"type": "redis", "status": "disconnected"}
            
        try:
            info = await self.redis_client.info()
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / max(1, total_requests)) * 100
            
            return {
                "type": "redis",
                "status": "connected",
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate_percent": round(hit_rate, 2),
                "redis_info": {
                    "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Redis stats error: {e}")
            return {"type": "redis", "status": "error", "error": str(e)}


class APICache:
    """Main cache manager for API responses."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("api-gateway.cache")
        
        # Initialize cache backend
        cache_type = config.get("type", "memory")
        
        if cache_type == "redis" and REDIS_AVAILABLE:
            self.cache = RedisCache(
                redis_url=config.get("redis_url", "redis://localhost:6379"),
                prefix=config.get("prefix", "api-gateway:")
            )
        else:
            self.cache = MemoryCache(
                max_size=config.get("max_size", 1000)
            )
            
        # Default TTL settings by endpoint type
        self.default_ttls = {
            "embeddings": 3600 * 24,  # 24 hours - embeddings rarely change
            "chat/completions": 300,   # 5 minutes - conversations are dynamic
            "images/generations": 3600 * 2,  # 2 hours - images for same prompt
            "models": 3600 * 6,       # 6 hours - model lists change infrequently
            "default": 1800           # 30 minutes
        }
        
    async def initialize(self):
        """Initialize cache connections."""
        if hasattr(self.cache, 'connect'):
            await self.cache.connect()
            
    def _generate_cache_key(self, provider: str, endpoint: str, data: Dict[str, Any]) -> str:
        """Generate a cache key for the request."""
        # Create deterministic hash of request parameters
        cache_data = {
            "provider": provider,
            "endpoint": endpoint,
            "data": data
        }
        
        # Sort keys for consistent hashing
        sorted_data = json.dumps(cache_data, sort_keys=True)
        
        # Generate short hash
        hash_obj = hashlib.md5(sorted_data.encode())
        return f"{provider}:{endpoint}:{hash_obj.hexdigest()[:16]}"
        
    def _should_cache(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Determine if request should be cached."""
        # Don't cache streaming requests
        if data.get("stream", False):
            return False
            
        # Don't cache requests with very high temperature (too random)
        if data.get("temperature", 1.0) > 1.5:
            return False
            
        # Don't cache requests that explicitly ask not to be cached
        if data.get("no_cache", False):
            return False
            
        return True
        
    async def get_cached_response(self, provider: str, endpoint: str, 
                                data: Dict[str, Any]) -> Optional[Any]:
        """Get cached response if available."""
        if not self._should_cache(endpoint, data):
            return None
            
        try:
            cache_key = self._generate_cache_key(provider, endpoint, data)
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                self.logger.info(f"Cache hit for {provider}:{endpoint}")
                return cached_data
                
        except Exception as e:
            self.logger.error(f"Cache get error: {e}")
            
        return None
        
    async def cache_response(self, provider: str, endpoint: str, 
                           data: Dict[str, Any], response: Any, 
                           cost_saved: float = 0.0) -> bool:
        """Cache an API response."""
        if not self._should_cache(endpoint, data):
            return False
            
        try:
            cache_key = self._generate_cache_key(provider, endpoint, data)
            ttl = self.default_ttls.get(endpoint, self.default_ttls["default"])
            
            # Custom TTL from request
            if "cache_ttl" in data:
                ttl = int(data["cache_ttl"])
                
            success = await self.cache.set(
                cache_key, 
                response, 
                ttl=ttl,
                provider=provider,
                cost_saved=cost_saved
            )
            
            if success:
                self.logger.info(f"Cached response for {provider}:{endpoint} (TTL: {ttl}s)")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Cache set error: {e}")
            return False
            
    async def invalidate(self, provider: str = None, endpoint: str = None) -> int:
        """Invalidate cache entries."""
        if provider is None and endpoint is None:
            # Clear all cache
            return await self.cache.clear()
        else:
            # For now, just return 0 - specific invalidation would need more complex key tracking
            self.logger.warning("Specific cache invalidation not yet implemented")
            return 0
            
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        return await self.cache.get_stats()
