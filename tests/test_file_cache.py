# tests/test_file_cache.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 file cache tests (25 tests).

import json
import time
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch


class TestFileCacheInit:
    """Tests for FileCache initialization."""
    
    def test_cache_importable(self):
        from kloudkompass.cache.file_cache import FileCache
        assert FileCache is not None
    
    def test_custom_cache_dir(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            assert cache.cache_dir == Path(tmpdir)
    
    def test_default_ttl(self):
        from kloudkompass.cache.file_cache import FileCache, DEFAULT_TTL
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            assert cache.ttl == DEFAULT_TTL
    
    def test_custom_ttl(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=60)
            assert cache.ttl == 60
    
    def test_creates_cache_dir(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "deep" / "nested"
            cache = FileCache(cache_dir=subdir)
            assert subdir.exists()


class TestFileCacheSetGet:
    """Tests for set/get operations."""
    
    def test_set_returns_true(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            assert cache.set("key1", {"data": "test"}) is True
    
    def test_get_returns_cached_value(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            cache.set("key1", {"data": "test"})
            result = cache.get("key1")
            assert result == {"data": "test"}
    
    def test_get_returns_none_for_missing(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            assert cache.get("nonexistent") is None
    
    def test_expired_entry_returns_none(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=0)
            cache.set("key1", "data", ttl=0)
            time.sleep(0.01)
            assert cache.get("key1") is None
    
    def test_set_with_ttl_override(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=1)
            cache.set("key1", "data", ttl=3600)
            assert cache.get("key1") == "data"
    
    def test_set_with_provider(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            cache.set("key1", "data", provider="aws")
            assert cache.get("key1") == "data"


class TestFileCacheInvalidate:
    """Tests for invalidation."""
    
    def test_invalidate_existing(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            cache.set("key1", "data")
            assert cache.invalidate("key1") is True
    
    def test_invalidate_nonexistent(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            assert cache.invalidate("nonexistent") is False
    
    def test_get_after_invalidate(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            cache.set("key1", "data")
            cache.invalidate("key1")
            assert cache.get("key1") is None


class TestFileCacheClear:
    """Tests for clear and cleanup."""
    
    def test_clear_returns_count(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            cache.set("k1", "v1")
            cache.set("k2", "v2")
            count = cache.clear()
            assert count == 2
    
    def test_clear_empty_cache(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            assert cache.clear() == 0
    
    def test_cleanup_expired(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir), ttl=0)
            cache.set("k1", "v1", ttl=0)
            time.sleep(0.01)
            count = cache.cleanup_expired()
            assert count >= 1


class TestFileCacheSize:
    """Tests for size property."""
    
    def test_empty_size(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            assert cache.size == 0
    
    def test_size_after_set(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            cache.set("k1", "v1")
            cache.set("k2", "v2")
            assert cache.size == 2
    
    def test_size_after_clear(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            cache.set("k1", "v1")
            cache.clear()
            assert cache.size == 0


class TestFileCacheMakeKey:
    """Tests for _make_key()."""
    
    def test_key_is_string(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            key = cache._make_key("aws", "cost")
            assert isinstance(key, str)
    
    def test_same_args_same_key(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            k1 = cache._make_key("aws", "cost", region="us-east-1")
            k2 = cache._make_key("aws", "cost", region="us-east-1")
            assert k1 == k2
    
    def test_different_args_different_key(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            k1 = cache._make_key("aws", "cost")
            k2 = cache._make_key("gcp", "cost")
            assert k1 != k2


class TestCorruptedCache:
    """Tests for corrupted cache file handling."""
    
    def test_corrupted_json_returns_none(self):
        from kloudkompass.cache.file_cache import FileCache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = FileCache(cache_dir=Path(tmpdir))
            # Write corrupted file
            path = cache._get_cache_path("corrupt")
            path.write_text("not json{{{")
            assert cache.get("corrupt") is None
