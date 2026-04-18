# tests/test_provider_setup_screen.py
# -------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 provider setup screen tests (15 tests).

import pytest
import inspect
from unittest.mock import patch, MagicMock


class TestProviderSetupScreenExists:
    """Tests that ProviderSetupScreen is properly defined."""
    
    def test_screen_importable(self):
        """ProviderSetupScreen should be importable."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        assert ProviderSetupScreen is not None
    
    def test_screen_is_subclass_of_screen(self):
        """ProviderSetupScreen must be a Screen subclass."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        from kloudkompass.tui.screens import Screen
        assert issubclass(ProviderSetupScreen, Screen)
    
    def test_screen_has_title(self):
        """ProviderSetupScreen should have title attribute."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        from kloudkompass.tui.screens import BRAND_TITLE
        assert ProviderSetupScreen.title == BRAND_TITLE


class TestLifecycleCompliance:
    """Tests that ProviderSetupScreen follows lifecycle contract."""
    
    def test_has_mount(self):
        """Must have mount() method."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        assert hasattr(ProviderSetupScreen, 'mount')
    
    def test_has_render(self):
        """Must have render() method."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        assert hasattr(ProviderSetupScreen, 'render')
    
    def test_has_handle_input(self):
        """Must have handle_input() method."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        assert hasattr(ProviderSetupScreen, 'handle_input')
    
    def test_handle_input_uses_get_input(self):
        """handle_input must use get_input(), not raw input()."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        source = inspect.getsource(ProviderSetupScreen.handle_input)
        assert 'get_input(' in source
        # Check no standalone input() calls (exclude handle_input def and get_input)
        for line in source.split('\n'):
            stripped = line.strip()
            if 'def handle_input' in stripped:
                continue
            if 'get_input(' in stripped:
                continue
            assert 'input(' not in stripped, f"Found raw input() in: {stripped}"


class TestScreenInitialization:
    """Tests for ProviderSetupScreen initialization."""
    
    @patch('kloudkompass.tui.provider_setup_screen.check_provider_ready')
    @patch('kloudkompass.tui.provider_setup_screen.get_setup_instructions')
    def test_accepts_provider(self, mock_setup, mock_ready):
        """Should accept provider string."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        
        mock_ready.return_value = ProviderSetupResult(success=False, provider="aws", error="CLI not found")
        mock_setup.return_value = {"provider": "aws", "cli_name": "aws", "cli_installed": False, "creds_valid": False, "cred_error": None, "install_instructions": "", "config_steps": []}
        
        screen = ProviderSetupScreen("aws")
        assert screen.provider == "aws"
    
    @patch('kloudkompass.tui.provider_setup_screen.check_provider_ready')
    @patch('kloudkompass.tui.provider_setup_screen.get_setup_instructions')
    def test_accepts_result(self, mock_setup, mock_ready):
        """Should accept pre-computed result."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        
        result = ProviderSetupResult(success=False, provider="aws", error="CLI not found")
        mock_setup.return_value = {"provider": "aws", "cli_name": "aws", "cli_installed": False, "creds_valid": False, "cred_error": None, "install_instructions": "", "config_steps": []}
        
        screen = ProviderSetupScreen("aws", result)
        assert screen.setup_result is result
        # Should NOT call check_provider_ready again
        mock_ready.assert_not_called()
    
    @patch('kloudkompass.tui.provider_setup_screen.check_provider_ready')
    @patch('kloudkompass.tui.provider_setup_screen.get_setup_instructions')
    def test_has_get_result(self, mock_setup, mock_ready):
        """Should have get_result() method."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        
        result = ProviderSetupResult(success=False, provider="aws", error="test")
        mock_setup.return_value = {"provider": "aws", "cli_name": "aws", "cli_installed": False, "creds_valid": False, "cred_error": None, "install_instructions": "", "config_steps": []}
        
        screen = ProviderSetupScreen("aws", result)
        assert screen.get_result() is result


class TestNoNavigationSemanticsAdded:
    """Tests that ProviderSetupScreen does not introduce new navigation."""
    
    def test_no_new_bindings(self):
        """Should not define custom key bindings."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        # Should not have BINDINGS attribute
        assert not hasattr(ProviderSetupScreen, 'BINDINGS')
    
    def test_uses_nav_hint(self):
        """render() should show NAV_HINT."""
        from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
        source = inspect.getsource(ProviderSetupScreen.render)
        assert 'NAV_HINT' in source
    
    def test_no_raw_input(self):
        """Module must not contain raw input() calls."""
        from kloudkompass.tui import provider_setup_screen
        source = inspect.getsource(provider_setup_screen)
        # Check for raw input() — exclude get_input, handle_input, and comments
        lines = source.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"') or stripped.startswith("'"):
                continue
            if 'def handle_input' in stripped:
                continue
            if 'get_input(' in stripped:
                continue
            if 'input(' in stripped:
                pytest.fail(f"Found raw input() in: {stripped}")
