# tests/test_screen_base.py
# ---------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 Screen base class tests (25 tests).

import pytest
import inspect
from unittest.mock import patch, MagicMock


class TestScreenConstants:
    """Tests for module-level constants."""
    
    def test_brand_title_exists(self):
        from kloudkompass.tui.screens import BRAND_TITLE
        assert BRAND_TITLE is not None
    
    def test_brand_short_exists(self):
        from kloudkompass.tui.screens import BRAND_SHORT
        assert BRAND_SHORT is not None
    
    def test_nav_hint_exists(self):
        from kloudkompass.tui.screens import NAV_HINT
        assert NAV_HINT is not None
    
    def test_brand_title_contains_kloudkompass(self):
        from kloudkompass.tui.screens import BRAND_TITLE
        assert "Kloud Kompass" in BRAND_TITLE
    
    def test_nav_hint_contains_back(self):
        from kloudkompass.tui.screens import NAV_HINT
        assert "B" in NAV_HINT
    
    def test_nav_hint_contains_quit(self):
        from kloudkompass.tui.screens import NAV_HINT
        assert "Q" in NAV_HINT


class TestInputResultClass:
    """Tests for InputResult dataclass."""
    
    def test_basic_creation(self):
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="test")
        assert result.raw == "test"
    
    def test_default_intent_none(self):
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="1")
        assert result.intent is None
    
    def test_quit_intent(self):
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="q", intent="quit")
        assert result.is_quit is True
    
    def test_back_intent(self):
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="b", intent="back")
        assert result.is_back is True
    
    def test_non_navigation_not_navigation(self):
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="1")
        assert result.is_navigation is False
    
    def test_quit_is_navigation(self):
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="q", intent="quit")
        assert result.is_navigation is True
    
    def test_back_is_navigation(self):
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="b", intent="back")
        assert result.is_navigation is True


class TestScreenClass:
    """Tests for Screen base class."""
    
    def test_screen_exists(self):
        from kloudkompass.tui.screens import Screen
        assert Screen is not None
    
    def test_screen_is_abstract(self):
        from kloudkompass.tui.screens import Screen
        with pytest.raises(TypeError):
            Screen()  # Cannot instantiate abstract class
    
    def test_has_get_input(self):
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'get_input')
    
    def test_has_display(self):
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'display')
    
    def test_has_run(self):
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'run')
    
    def test_has_print_header(self):
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'print_header')
    
    def test_has_print_nav_hint(self):
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'print_nav_hint')


class TestConfirmQuit:
    """Tests for confirm_quit() function."""
    
    def test_confirm_quit_exists(self):
        from kloudkompass.tui.screens import confirm_quit
        assert confirm_quit is not None
    
    @patch('builtins.input', return_value='y')
    def test_y_returns_true(self, mock_input):
        from kloudkompass.tui.screens import confirm_quit
        with patch('builtins.print'):
            assert confirm_quit() is True
    
    @patch('builtins.input', return_value='n')
    def test_n_returns_false(self, mock_input):
        from kloudkompass.tui.screens import confirm_quit
        with patch('builtins.print'):
            assert confirm_quit() is False
    
    @patch('builtins.input', return_value='')
    def test_empty_defaults_to_no(self, mock_input):
        from kloudkompass.tui.screens import confirm_quit
        with patch('builtins.print'):
            assert confirm_quit() is False
