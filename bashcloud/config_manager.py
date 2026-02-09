# bashcloud/config_manager.py
# ----------------------------
# persistent configuration handling. Users can set defaults like
# preferred provider, region, and output format. These are saved to
# ~/.bashcloud/config.toml and merged with CLI arguments.

import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    import toml
except ImportError:
    toml = None

from bashcloud.core.exceptions import ConfigurationError


# Default configuration location
CONFIG_DIR = Path.home() / ".bashcloud"
CONFIG_FILE = CONFIG_DIR / "config.toml"

# Default values for all configuration options
DEFAULT_CONFIG = {
    "default_provider": "aws",
    "default_region": None,
    "default_profile": None,
    "default_output": "table",
    "debug": False,
}


def ensure_config_dir() -> Path:
    """
    Create the config directory if it does not exist.
    
    Creates ~/.bashcloud to store configuration and any cached data.
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
    
    Writes the config in TOML format for human readability.
    """
    if toml is None:
        raise ConfigurationError(
            "Cannot save config: 'toml' package not installed.",
            config_path=str(CONFIG_FILE)
        )
    
    try:
        ensure_config_dir()
        with open(CONFIG_FILE, 'w') as f:
            toml.dump(config, f)
    except PermissionError:
        raise ConfigurationError(
            f"Permission denied writing to {CONFIG_FILE}",
            config_path=str(CONFIG_FILE)
        )
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
