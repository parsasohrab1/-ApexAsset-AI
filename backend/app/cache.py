"""
Cache layer for high-traffic endpoints.
Supports in-memory TTL cache (default) and optional Redis.
"""

import json
import time
import asyncio
from typing import Optional, Any
from threading import Lock

# Optional Redis
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class InMemoryTTLCache:
    """Simple in-memory cache with TTL. Thread-safe."""

    def __init__(self, ttl_seconds: int = 10, maxsize: int = 100):
        self.ttl = ttl_seconds
        self.maxsize = maxsize
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            value, expires_at = self._cache[key]
            if time.monotonic() > expires_at:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            if len(self._cache) >= self.maxsize and key not in self._cache:
                # Evict oldest
                oldest_key = min(
                    self._cache.keys(),
                    key=lambda k: self._cache[k][1]
                )
                del self._cache[oldest_key]
            self._cache[key] = (value, time.monotonic() + self.ttl)

    def delete(self, key: str) -> None:
        with self._lock:
            self._cache.pop(key, None)


class CacheBackend:
    """Unified cache backend - in-memory or Redis."""

    def __init__(
        self,
        redis_url: Optional[str] = None,
        ttl_seconds: int = 10,
        key_prefix: str = "apexasset:"
    ):
        self.ttl = ttl_seconds
        self.key_prefix = key_prefix
        self._redis: Optional[Any] = None
        self._use_redis = bool(redis_url and REDIS_AVAILABLE)
        self._redis_url = redis_url
        self._memory = InMemoryTTLCache(ttl_seconds=ttl_seconds, maxsize=200)

    async def _get_redis(self):
        if self._redis is None and self._use_redis:
            self._redis = aioredis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    def _key(self, name: str) -> str:
        return f"{self.key_prefix}{name}"

    async def get(self, key: str) -> Optional[Any]:
        if self._use_redis:
            try:
                r = await self._get_redis()
                data = await r.get(self._key(key))
                if data:
                    return json.loads(data)
            except Exception:
                pass
        return self._memory.get(key)

    async def set(self, key: str, value: Any) -> None:
        if self._use_redis:
            try:
                r = await self._get_redis()
                serialized = json.dumps(value, default=str)
                await r.setex(
                    self._key(key),
                    self.ttl,
                    serialized,
                )
            except Exception:
                pass
        self._memory.set(key, value)

    async def delete(self, key: str) -> None:
        """Invalidate cache for the given key."""
        if self._use_redis:
            try:
                r = await self._get_redis()
                await r.delete(self._key(key))
            except Exception:
                pass
        self._memory.delete(key)

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None


# Global cache instance
_cache: Optional[CacheBackend] = None


def get_cache() -> CacheBackend:
    """Get or create the global cache backend."""
    global _cache
    if _cache is None:
        from .config import settings
        redis_url = getattr(settings, "REDIS_URL", None) or ""
        ttl = int(getattr(settings, "DASHBOARD_CACHE_TTL_SECONDS", 10))
        _cache = CacheBackend(
            redis_url=redis_url if redis_url else None,
            ttl_seconds=ttl,
        )
    return _cache
