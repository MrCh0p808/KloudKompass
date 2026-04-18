# tests/test_cache_lru.py
# ------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Tests for LRU cache eviction per Master Brief cache hardening.

import pytest
import time

from kloudkompass.infra.cache import ResultCache


class TestCacheLRUEviction:
    """Tests for LRU eviction behavior."""
    
    def test_evicts_when_max_exceeded(self):
        """Should evict when max_entries exceeded."""
        cache = ResultCache(ttl=300, max_entries=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # Should trigger eviction
        
        assert cache.size == 3
        # key1 should be evicted (oldest)
        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
    
    def test_evicts_least_recently_used(self):
        """Should evict entry with oldest last_accessed."""
        cache = ResultCache(ttl=300, max_entries=3)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Access key1, making key2 least recently used
        cache.get("key1")
        cache.get("key3")
        
        cache.set("key4", "value4")  # Should evict key2
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None  # Evicted
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_update_does_not_count_as_new_entry(self):
        """Updating existing key should not trigger eviction."""
        cache = ResultCache(ttl=300, max_entries=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key1", "updated")  # Update, not new
        
        assert cache.size == 2
        assert cache.get("key1") == "updated"
        assert cache.get("key2") == "value2"


class TestCacheMaxEntries:
    """Tests for max entries enforcement."""
    
    def test_respects_max_entries(self):
        """Cache should never exceed max_entries."""
        cache = ResultCache(ttl=300, max_entries=5)
        
        for i in range(10):
            cache.set(f"key{i}", f"value{i}")
        
        assert cache.size == 5
    
    def test_default_max_entries(self):
        """Default max_entries should be 100."""
        cache = ResultCache()
        
        assert cache.max_entries == 100


class TestCacheLastAccessed:
    """Tests for last_accessed tracking."""
    
    def test_get_updates_last_accessed(self):
        """get() should update last_accessed."""
        cache = ResultCache(ttl=300, max_entries=2)
        
        cache.set("key1", "value1")
        time.sleep(0.01)
        cache.set("key2", "value2")
        
        # Access key1, making it more recent than key2
        cache.get("key1")
        
        # Add new entry, should evict key2
        cache.set("key3", "value3")
        
        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
    
    def test_set_updates_last_accessed(self):
        """set() should set last_accessed to now."""
        cache = ResultCache(ttl=300, max_entries=10)
        
        cache.set("key1", "value1")
        
        # Internal check - entry should have last_accessed
        entry = cache._cache.get("key1")
        assert entry is not None
        assert entry.last_accessed > 0


class TestCacheDebugVisibility:
    """Tests for debug visibility feature."""
    
    def test_stats_empty_when_debug_disabled(self):
        """get_stats should return empty when debug disabled."""
        cache = ResultCache()
        cache.set("key", "value")
        
        stats = cache.get_stats()
        
        assert stats == {}
    
    def test_stats_populated_when_debug_enabled(self):
        """get_stats should return data when debug enabled."""
        cache = ResultCache(ttl=300, max_entries=10)
        cache.set_debug(True)
        cache.set("key", "value")
        
        stats = cache.get_stats()
        
        assert stats["size"] == 1
        assert stats["max_entries"] == 10
        assert stats["ttl"] == 300
        assert len(stats["entries"]) == 1


class TestCacheDeterministicEviction:
    """Tests for deterministic eviction order."""
    
    def test_eviction_order_is_deterministic(self):
        """Eviction should be deterministic based on timestamps."""
        cache = ResultCache(ttl=300, max_entries=3)
        
        # Add entries with controlled timing
        cache.set("a", "1")
        time.sleep(0.01)
        cache.set("b", "2")
        time.sleep(0.01)
        cache.set("c", "3")
        
        # Add more entries
        cache.set("d", "4")  # Evicts "a"
        cache.set("e", "5")  # Evicts "b"
        
        assert cache.get("a") is None
        assert cache.get("b") is None
        assert cache.get("c") == "3"
        assert cache.get("d") == "4"
        assert cache.get("e") == "5"
