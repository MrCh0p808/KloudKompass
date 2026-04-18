# kloudkompass/core/keymap.py
# ---------------------------
# Customizable hotkey mappings loader (Feature 45).
# Users can override default keybindings by placing a
# ~/.kloudkompass/keymap.json file with { "action_name": "key" } entries.

import json
from pathlib import Path
from typing import Dict, Optional

from kloudkompass.config_manager import CONFIG_DIR


KEYMAP_FILE = CONFIG_DIR / "keymap.json"

# Default keymap that ships with the application
DEFAULT_KEYMAP: Dict[str, str] = {
    "quit": "q",
    "export": "e",
    "refresh": "r",
    "force_refresh": "f5",
    "toggle_dark": "d",
    "toggle_sidebar": "[",
    "show_help": "?",
    "show_cost": "1",
    "show_compute": "2",
    "show_network": "3",
    "show_storage": "4",
    "show_iam": "5",
    "show_database": "6",
    "show_security": "7",
    "show_doctor": "8",
    "search_focus": "/",
    "clear_filter": "escape",
    "start_instance": "ctrl+s",
    "stop_instance": "ctrl+x",
    "terminate_instance": "shift+t",
    "copy_id": "c",
    "copy_json": "ctrl+c",
    "toggle_select": "space",
    "resolve_vpc": "v",
    "open_in_browser": "o",
    "ignore_finding": "i",
    "start_rds": "ctrl+s",
    "stop_rds": "ctrl+x",
}


def load_keymap() -> Dict[str, str]:
    """
    Load user keymap overrides from ~/.kloudkompass/keymap.json.

    Returns the merged keymap (defaults + user overrides).
    """
    keymap = DEFAULT_KEYMAP.copy()

    if not KEYMAP_FILE.exists():
        return keymap

    try:
        with open(KEYMAP_FILE, "r", encoding="utf-8") as f:
            user_overrides = json.load(f)

        if isinstance(user_overrides, dict):
            keymap.update(user_overrides)
    except Exception:
        # If keymap.json is corrupted, silently fall back to defaults
        pass

    return keymap


def save_default_keymap() -> None:
    """
    Write the default keymap to disk so users can see and edit it.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(KEYMAP_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_KEYMAP, f, indent=2)


def get_key(action: str) -> Optional[str]:
    """
    Get the keybinding for a specific action.
    """
    keymap = load_keymap()
    return keymap.get(action)
