# kloudkompass/config_manager.py
# ----------------------------
# persistent configuration handling. Users can set defaults like
# preferred provider, region, and output format. These are saved to
# ~/.kloudkompass/config.toml and merged with CLI arguments.

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import toml
except ImportError:
    toml = None

from kloudkompass.core.exceptions import ConfigurationError


# Default configuration location
CONFIG_DIR = Path.home() / ".kloudkompass"
CONFIG_FILE = CONFIG_DIR / "config.toml"

# Default values for all configuration options
DEFAULT_CONFIG = {
    "default_provider": "aws",
    "default_region": None,
    "default_profile": None,
    "default_output": "table",
    "debug": False,
    "cache_ttl_seconds": 300,
}


def ensure_config_dir() -> Path:
    """
    Create the config directory if it does not exist.
    
    Creates ~/.kloudkompass to store configuration and any cached data.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Returns the merged default config with any user overrides.
    If no config file exists, returns defaults.
    """
    config = DEFAULT_CONFIG.copy()
    
    if not CONFIG_FILE.exists():
        return config
    
    if toml is None:
        # toml not installed, just use defaults
        return config
    
    try:
        user_config = toml.load(CONFIG_FILE)
        # Merge user config over defaults
        config.update(user_config)
        return config
    except Exception as e:
        raise ConfigurationError(
            f"Failed to parse config file: {e}",
            config_path=str(CONFIG_FILE)
        )


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to file.
    
    M1 FIX: Uses atomic writes via tempfile + os.replace to prevent
    concurrent tab writes from corrupting the config file.
    """
    if toml is None:
        raise ConfigurationError(
            "Cannot save config: 'toml' package not installed.",
            config_path=str(CONFIG_FILE)
        )
    
    import tempfile
    
    try:
        ensure_config_dir()
        # Write to a temp file first, then atomically replace
        fd, temp_path = tempfile.mkstemp(
            dir=CONFIG_DIR, prefix=".config_tmp_", suffix=".toml"
        )
        try:
            with os.fdopen(fd, 'w') as f:
                toml.dump(config, f)
            os.replace(temp_path, CONFIG_FILE)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
    except PermissionError:
        raise ConfigurationError(
            f"Permission denied writing to {CONFIG_FILE}",
            config_path=str(CONFIG_FILE)
        )
    except ConfigurationError:
        raise
    except Exception as e:
        raise ConfigurationError(
            f"Failed to save config: {e}",
            config_path=str(CONFIG_FILE)
        )


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a single configuration value.
    
    Convenience function for getting one value without loading entire config.
    """
    config = load_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """
    Set a single configuration value and save.
    
    Convenience function for updating one value.
    """
    config = load_config()
    config[key] = value
    save_config(config)


def merge_cli_with_config(
    provider: Optional[str] = None,
    profile: Optional[str] = None,
    region: Optional[str] = None,
    output: Optional[str] = None,
    debug: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Merge CLI arguments with saved configuration.
    
    CLI arguments take precedence over saved config.
    This is the main function CLI uses to get effective settings.
    
    Returns a dict with all settings resolved:
    - provider
    - profile
    - region
    - output
    - debug
    """
    config = load_config()
    
    return {
        "provider": provider or config.get("default_provider", "aws"),
        "profile": profile or config.get("default_profile"),
        "region": region or config.get("default_region"),
        "output": output or config.get("default_output", "table"),
        "debug": debug if debug is not None else config.get("debug", False),
    }


def get_config_path() -> str:
    """Return the path to the config file."""
    return str(CONFIG_FILE)


def config_exists() -> bool:
    """Check if a config file exists."""
    return CONFIG_FILE.exists()
