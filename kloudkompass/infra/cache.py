# kloudkompass/infra/cache.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# In-memory TTL cache with LRU eviction. Prevents unbounded memory growth
# per Master Brief cache hardening requirements.

import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, List
from functools import wraps


@dataclass
class CacheEntry:
    """
    A cached result with expiration time and access tracking.
    
    Stores the value with expiry time and last access for LRU eviction.
    """
    value: Any
    expires_at: float
    last_accessed: float = field(default_factory=time.time)
    
    @property
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return time.time() > self.expires_at
    
    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = time.time()


class ResultCache:
    """
    In-memory TTL cache with LRU eviction.
    
    Features:
    - TTL-based expiration
    - Max entries with LRU eviction
    - SHA-256 key hashing (stable and deterministic)
    - Debug visibility (optional)
    
    Invariant:
        - Cache must never mask errors
        - Eviction is deterministic (oldest access first)
    """
    
    # Default configuration
    DEFAULT_TTL = 300  # 5 minutes
    DEFAULT_MAX_ENTRIES = 100
    
    def __init__(
        self,
        ttl: int = DEFAULT_TTL,
        max_entries: int = DEFAULT_MAX_ENTRIES,
    ):
        """
        Create a cache with specified TTL and max entries.
        
        Args:
            ttl: Time-to-live in seconds for cached entries
            max_entries: Maximum number of entries before LRU eviction
        """
        self.ttl = ttl
        self.max_entries = max_entries
        self._cache: Dict[str, CacheEntry] = {}
        self._debug = False
    
    def set_debug(self, enabled: bool) -> None:
        """Enable or disable debug visibility."""
        self._debug = enabled
    
    def _make_key(self, *args, **kwargs) -> str:
        """
        Generate a cache key from function arguments.
        
        Uses SHA-256 for stable, deterministic key hashing.
        """
        key_data = {
            "args": args,
            "kwargs": sorted(kwargs.items()),
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def _evict_lru(self) -> None:
        """
        Evict the least recently used entry.
        
        Called when cache exceeds max_entries. Eviction is deterministic
        based on last_accessed timestamp.
        """
        if not self._cache:
            return
        
        # Find entry with oldest last_accessed
        oldest_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        del self._cache[oldest_key]
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Updates last_accessed on hit. Returns None if not found or expired.
        """
        entry = self._cache.get(key)
        
        if entry is None:
            return None
        
        if entry.is_expired:
            del self._cache[key]
            return None
        
        # Update access time for LRU tracking
        entry.touch()
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in the cache.
        
        Triggers LRU eviction if max_entries would be exceeded.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Optional TTL override
        """
        # Evict if at capacity and this is a new key
        if key not in self._cache and len(self._cache) >= self.max_entries:
            self._evict_lru()
        
        effective_ttl = ttl if ttl is not None else self.ttl
        expires_at = time.time() + effective_ttl
        
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=expires_at,
            last_accessed=time.time(),
        )
    
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
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics for debug visibility.
        
        Only available when debug mode is enabled.
        """
        if not self._debug:
            return {}
        
        now = time.time()
        entries = []
        for key, entry in self._cache.items():
            entries.append({
                "key": key,
                "expired": entry.is_expired,
                "age_seconds": now - (entry.expires_at - self.ttl),
                "last_accessed_ago": now - entry.last_accessed,
            })
        
        return {
            "size": self.size,
            "max_entries": self.max_entries,
            "ttl": self.ttl,
            "entries": entries,
        }


# Global cache instance for cost queries
_cost_cache = ResultCache()


def cache_result(ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    
    Wraps provider methods so repeated calls with the
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
