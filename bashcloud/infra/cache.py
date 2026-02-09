# bashcloud/infra/cache.py
# -------------------------
# a simple TTL-based cache This avoids hitting cloud APIs
# repeatedly for the same query. Especially useful in dashboard mode where
# the user might switch views and come back.

import time
import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Callable
from functools import wraps


@dataclass
class CacheEntry:
    """
    A cached result with expiration time.
    
    Stores the value with expiry time for freshness.
    """
    value: Any
    expires_at: float
    
    @property
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return time.time() > self.expires_at


class ResultCache:
    """
    Simple in-memory TTL cache for query results.
    
    This to avoid repeated API calls for the same query parameters.
    The cache is keyed by a hash of the query parameters.
    """
    
    # Default TTL in seconds (5 minutes)
    DEFAULT_TTL = 300
    
    def __init__(self, ttl: int = DEFAULT_TTL):
        """
        Create a cache with specified TTL.
        
        Args:
            ttl: Time-to-live in seconds for cached entries
        """
        self.ttl = ttl
        self._cache: Dict[str, CacheEntry] = {}
    
    def _make_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments.
        
        Hashes the arguments to create a consistent key regardless of
        argument order.
        """
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()),
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Returns None if not found or expired.
        """
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired:
            del self._cache[key]
            return None
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Optional TTL override
        """
        effective_ttl = ttl if ttl is not None else self.ttl
        expires_at = time.time() + effective_ttl
        
        self._cache[key] = CacheEntry(value=value, expires_at=expires_at)
    
    def invalidate(self, key: str) -> None:
        """Remove a specific entry from the cache."""
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns the number of entries removed.
        """
        expired_keys = [
            k for k, v in self._cache.items() if v.is_expired
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    @property
    def size(self) -> int:
        """Number of entries in the cache."""
        return len(self._cache)


# Global cache instance for cost queries
_cost_cache = ResultCache()


def cache_result(ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    This to wrap provider methods so repeated calls with the
    same arguments return cached results.
    
    Example:
        @cache_result(ttl=600)
        def get_cost_by_service(self, start, end):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Skip 'self' in cache key
            cache_args = args[1:] if args else args
            key = _cost_cache._make_key(func.__name__, *cache_args, **kwargs)
            
            cached = _cost_cache.get(key)
            if cached is not None:
                return cached
            
            result = func(*args, **kwargs)
            _cost_cache.set(key, result, ttl)
            return result
        
        # Attach cache control methods
        wrapper.cache_clear = _cost_cache.clear
        wrapper.cache_invalidate = lambda: None  # Per-function clear TBD
        
        return wrapper
    return decorator


def get_cost_cache() -> ResultCache:
    """Get the global cost query cache."""
    return _cost_cache
