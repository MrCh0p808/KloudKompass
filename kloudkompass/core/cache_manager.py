import json
import os
import time
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

from kloudkompass.config_manager import CONFIG_DIR


CACHE_DIR = CONFIG_DIR / "cache"


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects returned by cloud SDKs."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def _sanitize_key(key: str) -> str:
    """
    Sanitize the cache key to prevent path traversal vulnerabilities (S1).
    Strips path separators and restricts to safe characters.
    """
    import re
    # Remove any path separators or null bytes
    clean = re.sub(r'[\\/\x00]', '', key)
    # Remove parent directory references
    clean = clean.replace('..', '')
    # Trim to reasonable length and restrict characters
    clean = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', clean)
    return clean[:255]


def ensure_cache_dir() -> Path:
    """
    Ensure the cache directory exists with strict 0o700 permissions
    to prevent cross-user access of cloud metadata on shared instances.
    """
    if not CACHE_DIR.exists():
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # Enforce strict rwx------ permissions on the directory
        os.chmod(CACHE_DIR, 0o700)
    return CACHE_DIR


def get_cache(key: str, max_age_seconds: int = 300) -> Optional[Any]:
    """
    Retrieve data from the cache if it exists and is younger than max_age_seconds.
    """
    ensure_cache_dir()
    safe_key = _sanitize_key(key)
    cache_file = CACHE_DIR / f"{safe_key}.json"
    
    if not cache_file.exists():
        return None
        
    try:
        # Check file age (mtime)
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > max_age_seconds:
            return None
            
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # If the file is corrupted or unreadable, treat it as a cache miss
        return None


def set_cache(key: str, data: Any) -> None:
    """
    Store python data to the cache JSON file with strict 0o600 permissions.
    Uses atomic writes with tempfile + replace to prevent corruption (Gap 2).
    """
    import tempfile
    ensure_cache_dir()
    safe_key = _sanitize_key(key)
    cache_file = CACHE_DIR / f"{safe_key}.json"
    
    try:
        # Create a temporary file in the same directory as the cache
        fd, temp_path = tempfile.mkstemp(dir=CACHE_DIR, prefix=f".tmp_{safe_key}_", suffix=".json")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data, f, cls=DateTimeEncoder)
            
            # Secure the temp file (rw-------)
            os.chmod(temp_path, 0o600)
            
            # Atomically replace the old cache file with the new one
            os.replace(temp_path, cache_file)
        except Exception:
            # Cleanup temp file on failure
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    except Exception as e:
        import logging
        logging.getLogger('kloudkompass').warning(f"Failed to write cache {key}: {e}")


def clear_cache(key: Optional[str] = None) -> None:
    """
    Delete a specific cache key, or entirely clear the cache directory.
    """
    if not CACHE_DIR.exists():
        return
        
    if key:
        safe_key = _sanitize_key(key)
        cache_file = CACHE_DIR / f"{safe_key}.json"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except OSError:
                pass
    else:
        # Clear all JSON files in the cache dir
        for cache_file in CACHE_DIR.glob("*.json"):
            try:
                cache_file.unlink()
            except OSError:
                pass


def cached(key_prefix: str, max_age_seconds: int = 300):
    """
    Decorator to automatically cache the JSON-serializable output of provider API methods.
    
    Dynamically builds a cache key using the prefix, profile, and region kwargs.
    Filters/tags inside kwargs are skipped for simplicity in the basic key name,
    but we can serialize kwargs natively if needed.
    """
    import functools
    import hashlib
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract basic context parameters
            profile = kwargs.get('profile', 'default') or 'default'
            region = kwargs.get('region', 'default') or 'default'
            
            # Serialize the remaining kwargs to keep the cache key unique for different filters
            safe_kwargs = {k: v for k, v in kwargs.items() if k not in ['profile', 'region'] and v}
            kwarg_hash = ""
            if safe_kwargs:
                kwarg_str = json.dumps(safe_kwargs, sort_keys=True)
                kwarg_hash = "_" + hashlib.sha256(kwarg_str.encode()).hexdigest()[:8]  # L2 FIX
                
            cache_key = f"{key_prefix}_{profile}_{region}{kwarg_hash}"
            
            data = get_cache(cache_key, max_age_seconds)
            if data is not None:
                return data
                
            # Cache miss - execute real AWS CLI function
            result = func(*args, **kwargs)
            
            # Save it
            if result is not None:
                set_cache(cache_key, result)
                
            return result
        return wrapper
    return decorator
