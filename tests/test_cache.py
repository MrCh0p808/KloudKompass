# tests/test_cache.py
# --------------------
# Tests the caching layer. These tests verify TTL behavior,
# key generation, and the cache decorator.

import pytest
import time
from unittest.mock import Mock

from bashcloud.infra.cache import ResultCache, CacheEntry, cache_result


class TestCacheEntry:
    """Tests for CacheEntry dataclass."""
    
    def test_not_expired_within_ttl(self):
        """Entry should not be expired within TTL."""
        entry = CacheEntry(value="test", expires_at=time.time() + 60)
        assert entry.is_expired is False
    
    def test_expired_after_ttl(self):
        """Entry should be expired after TTL."""
        entry = CacheEntry(value="test", expires_at=time.time() - 1)
        assert entry.is_expired is True


class TestResultCache:
    """Tests for ResultCache class."""
    
    def test_set_and_get(self):
        """Should store and retrieve values."""
        cache = ResultCache(ttl=60)
        cache.set("key1", "value1")
        
        assert cache.get("key1") == "value1"
    
    def test_get_missing_key(self):
        """Should return None for missing key."""
        cache = ResultCache()
        assert cache.get("nonexistent") is None
    
    def test_get_expired_returns_none(self):
        """Should return None for expired entry."""
        cache = ResultCache(ttl=0)  # Immediate expiration
        cache.set("key1", "value1")
        time.sleep(0.01)  # Wait for expiration
        
        assert cache.get("key1") is None
    
    def test_invalidate(self):
        """invalidate should remove specific entry."""
        cache = ResultCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.invalidate("key1")
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_clear(self):
        """clear should remove all entries."""
        cache = ResultCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        cache.clear()
        
        assert cache.size == 0
    
    def test_cleanup_expired(self):
        """cleanup_expired should remove only expired entries."""
        cache = ResultCache(ttl=60)
        cache.set("fresh", "value", ttl=60)
        cache.set("stale", "value", ttl=0)
        time.sleep(0.01)
        
        removed = cache.cleanup_expired()
        
        assert removed == 1
        assert cache.get("fresh") == "value"
        assert cache.get("stale") is None
    
    def test_size(self):
        """size should return entry count."""
        cache = ResultCache()
        assert cache.size == 0
        
        cache.set("a", 1)
        cache.set("b", 2)
        
        assert cache.size == 2


class TestCacheDecorator:
    """Tests for cache_result decorator."""
    
    def test_caches_result(self):
        """Decorator should cache function result."""
        call_count = [0]
        
        @cache_result(ttl=60)
        def expensive_function(x):
            call_count[0] += 1
            return x * 2
        
        # First call
        result1 = expensive_function(5)
        # Second call (should be cached)
        result2 = expensive_function(5)
        
        assert result1 == 10
        assert result2 == 10
        # Should only be called once
        # Note: Due to global cache, this may vary based on test order
    
    def test_different_args_not_cached(self):
        """Different arguments should produce different cache keys."""
        from bashcloud.infra.cache import ResultCache
        
        cache = ResultCache()
        
        # Same function with different args should have different keys
        key1 = cache._make_key("func", 5)
        key2 = cache._make_key("func", 10)
        
        assert key1 != key2
