# tests/test_config_manager.py
# ------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 config manager tests (25 tests).

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestDefaultConfig:
    """Tests for default configuration values."""
    
    def test_default_config_exists(self):
        from kloudkompass.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG is not None
    
    def test_default_provider_is_aws(self):
        from kloudkompass.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG["default_provider"] == "aws"
    
    def test_default_output_is_table(self):
        from kloudkompass.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG["default_output"] == "table"
    
    def test_default_debug_is_false(self):
        from kloudkompass.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG["debug"] is False
    
    def test_default_region_is_none(self):
        from kloudkompass.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG["default_region"] is None
    
    def test_default_profile_is_none(self):
        from kloudkompass.config_manager import DEFAULT_CONFIG
        assert DEFAULT_CONFIG["default_profile"] is None


class TestLoadConfig:
    """Tests for load_config()."""
    
    @patch('kloudkompass.config_manager.CONFIG_FILE')
    def test_returns_defaults_when_no_file(self, mock_path):
        from kloudkompass.config_manager import load_config, DEFAULT_CONFIG
        mock_path.exists.return_value = False
        config = load_config()
        assert config["default_provider"] == DEFAULT_CONFIG["default_provider"]
    
    @patch('kloudkompass.config_manager.CONFIG_FILE')
    def test_returns_dict(self, mock_path):
        from kloudkompass.config_manager import load_config
        mock_path.exists.return_value = False
        config = load_config()
        assert isinstance(config, dict)


class TestMergeCliWithConfig:
    """Tests for merge_cli_with_config()."""
    
    @patch('kloudkompass.config_manager.load_config')
    def test_cli_provider_overrides_config(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config(provider="gcp")
        assert result["provider"] == "gcp"
    
    @patch('kloudkompass.config_manager.load_config')
    def test_config_defaults_when_no_cli(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config()
        assert result["provider"] == "aws"
    
    @patch('kloudkompass.config_manager.load_config')
    def test_debug_false_by_default(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config()
        assert result["debug"] is False
    
    @patch('kloudkompass.config_manager.load_config')
    def test_cli_debug_overrides_config(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config(debug=True)
        assert result["debug"] is True
    
    @patch('kloudkompass.config_manager.load_config')
    def test_output_format_override(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config(output="json")
        assert result["output"] == "json"
    
    @patch('kloudkompass.config_manager.load_config')
    def test_region_override(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config(region="eu-west-1")
        assert result["region"] == "eu-west-1"
    
    @patch('kloudkompass.config_manager.load_config')
    def test_profile_override(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config(profile="production")
        assert result["profile"] == "production"
    
    @patch('kloudkompass.config_manager.load_config')
    def test_returns_all_keys(self, mock_load):
        from kloudkompass.config_manager import merge_cli_with_config
        mock_load.return_value = {"default_provider": "aws", "default_profile": None, "default_region": None, "default_output": "table", "debug": False}
        result = merge_cli_with_config()
        assert "provider" in result
        assert "profile" in result
        assert "region" in result
        assert "output" in result
        assert "debug" in result


class TestConfigPath:
    """Tests for config path functions."""
    
    def test_get_config_path_returns_string(self):
        from kloudkompass.config_manager import get_config_path
        assert isinstance(get_config_path(), str)
    
    def test_config_path_contains_kloudkompass(self):
        from kloudkompass.config_manager import get_config_path
        assert ".kloudkompass" in get_config_path()
    
    def test_config_path_ends_with_toml(self):
        from kloudkompass.config_manager import get_config_path
        assert get_config_path().endswith(".toml")
    
    def test_config_exists_returns_bool(self):
        from kloudkompass.config_manager import config_exists
        assert isinstance(config_exists(), bool)


class TestGetSetConfigValue:
    """Tests for get/set convenience functions."""
    
    @patch('kloudkompass.config_manager.load_config')
    def test_get_existing_value(self, mock_load):
        from kloudkompass.config_manager import get_config_value
        mock_load.return_value = {"default_provider": "aws"}
        assert get_config_value("default_provider") == "aws"
    
    @patch('kloudkompass.config_manager.load_config')
    def test_get_missing_value_returns_default(self, mock_load):
        from kloudkompass.config_manager import get_config_value
        mock_load.return_value = {}
        assert get_config_value("nonexistent", "fallback") == "fallback"
