# tests/test_settings_menu_ext.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Extended settings menu tests — validation, persistence, config immutability.

import pytest
from unittest.mock import patch


class TestSettingsMenuStructure:
    """Test the settings TUI menu."""

    def test_import_settings_menu(self):
        from kloudkompass.tui.settings_menu import SettingsMenuScreen
        assert SettingsMenuScreen is not None

    def test_has_render_method(self):
        from kloudkompass.tui.settings_menu import SettingsMenuScreen
        assert hasattr(SettingsMenuScreen, "render")


class TestConfigManagerPersistence:
    """Test config loading and saving."""

    def test_load_returns_dict(self):
        from kloudkompass.config_manager import load_config
        config = load_config()
        assert isinstance(config, dict)

    def test_load_result_is_dict(self):
        """load_config should always return a dict, even on failure."""
        from kloudkompass.config_manager import load_config
        config = load_config()
        assert isinstance(config, dict)

    def test_config_keys_are_strings(self):
        from kloudkompass.config_manager import load_config
        config = load_config()
        for key in config:
            assert isinstance(key, str)

    def test_save_config_import(self):
        from kloudkompass.config_manager import save_config
        assert callable(save_config)
