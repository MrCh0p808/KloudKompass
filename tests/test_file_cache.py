# tests/test_file_cache.py
# -------------------------
# I test the file-based cache including TTL, hit/miss behavior,
# and cache cleanup.

import pytest
import json
import time
from pathlib import Path
from tempfile import TemporaryDirectory

from bashcloud.cache.file_cache import FileCache


class TestFileCacheBasic:
    """Tests for basic cache operations."""
    
    def test_set_and_get(self):
        """Should store and retrieve values."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            cache.set("test_key", {"foo": "bar"}, provider="test")
            result = cache.get("test_key")
            assert result == {"foo": "bar"}
    
    def test_get_nonexistent_returns_none(self):
        """Should return None for missing keys."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            result = cache.get("nonexistent")
            assert result is None
    
    def test_make_key_consistent(self):
        """Should generate consistent keys for same input."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            key1 = cache._make_key("aws", "2024-01-01", "2024-02-01", breakdown="service")
            key2 = cache._make_key("aws", "2024-01-01", "2024-02-01", breakdown="service")
            assert key1 == key2
    
    def test_make_key_different_for_different_input(self):
        """Should generate different keys for different input."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            key1 = cache._make_key("aws", "2024-01-01", "2024-02-01")
            key2 = cache._make_key("aws", "2024-01-01", "2024-03-01")
            assert key1 != key2


class TestFileCacheTTL:
    """Tests for TTL (time-to-live) behavior."""
    
    def test_expired_entry_returns_none(self):
        """Should return None for expired entries."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=0)  # Immediate expiry
            cache.set("test_key", "value", provider="test")
            time.sleep(0.1)  # Wait for expiry
            result = cache.get("test_key")
            assert result is None
    
    def test_custom_ttl_override(self):
        """Should respect custom TTL on set."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            cache.set("test_key", "value", provider="test", ttl=0)  # Override to immediate
            time.sleep(0.1)
            result = cache.get("test_key")
            assert result is None


class TestFileCacheInvalidation:
    """Tests for cache invalidation."""
    
    def test_invalidate_removes_entry(self):
        """Should remove specific entry."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            cache.set("key1", "value1", provider="test")
            cache.set("key2", "value2", provider="test")
            cache.invalidate("key1")
            
            # I assert inside the context
            assert cache.get("key1") is None
            assert cache.get("key2") == "value2"
    
    def test_clear_removes_all_entries(self):
        """Should remove all entries."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            cache.set("key1", "value1", provider="test")
            cache.set("key2", "value2", provider="test")
            removed = cache.clear()
            
            assert removed == 2
            assert cache.size == 0
    
    def test_cleanup_expired_removes_old_entries(self):
        """Should remove only expired entries."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            
            # Fresh entry
            cache.set("fresh", "value", provider="test", ttl=300)
            
            # I manually create an expired entry
            cache_path = cache._get_cache_path("expired")
            expired_data = {
                "value": "old",
                "expires_at": time.time() - 100,  # Expired 100 seconds ago
            }
            with open(cache_path, "w") as f:
                json.dump(expired_data, f)
            
            removed = cache.cleanup_expired()
            
            # I assert inside the context
            assert removed == 1
            assert cache.get("fresh") == "value"


class TestFileCacheSize:
    """Tests for cache size tracking."""
    
    def test_size_reflects_entry_count(self):
        """Should track number of entries."""
        with TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=300)
            
            assert cache.size == 0
            
            cache.set("key1", "value1", provider="test")
            assert cache.size == 1
            
            cache.set("key2", "value2", provider="test")
            assert cache.size == 2
            
            cache.invalidate("key1")
            assert cache.size == 1
