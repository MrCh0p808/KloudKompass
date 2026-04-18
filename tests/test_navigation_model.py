# tests/test_navigation_model.py
# -------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 navigation model tests.

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO


class TestInputResult:
    """Tests for InputResult dataclass."""
    
    def test_input_result_exists(self):
        """InputResult should be importable."""
        from kloudkompass.tui.screens import InputResult
        assert InputResult is not None
    
    def test_input_result_raw_field(self):
        """InputResult should have raw field."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="test")
        assert result.raw == "test"
    
    def test_input_result_intent_field(self):
        """InputResult should have intent field."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="q", intent="quit")
        assert result.intent == "quit"
    
    def test_input_result_is_navigation_true_for_quit(self):
        """is_navigation should be True for quit intent."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="q", intent="quit")
        assert result.is_navigation is True
    
    def test_input_result_is_navigation_true_for_back(self):
        """is_navigation should be True for back intent."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="b", intent="back")
        assert result.is_navigation is True
    
    def test_input_result_is_navigation_false_for_regular(self):
        """is_navigation should be False for regular input."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="1")
        assert result.is_navigation is False
    
    def test_input_result_is_quit(self):
        """is_quit should detect quit intent."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="q", intent="quit")
        assert result.is_quit is True
        assert result.is_back is False
    
    def test_input_result_is_back(self):
        """is_back should detect back intent."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="b", intent="back")
        assert result.is_back is True
        assert result.is_quit is False


class TestScreenGetInput:
    """Tests for Screen.get_input() method."""
    
    def test_get_input_exists(self):
        """Screen should have get_input method."""
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'get_input')
    
    def test_get_input_returns_input_result(self):
        """get_input should return InputResult."""
        from kloudkompass.tui.screens import Screen, InputResult
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="1"):
            result = screen.get_input()
        
        assert isinstance(result, InputResult)
    
    def test_get_input_detects_quit_lowercase(self):
        """get_input should detect 'q' as quit."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="q"):
            result = screen.get_input()
        
        assert result.intent == "quit"
        assert result.is_quit is True
    
    def test_get_input_detects_quit_uppercase(self):
        """get_input should detect 'Q' as quit."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="Q"):
            result = screen.get_input()
        
        assert result.intent == "quit"
    
    def test_get_input_detects_quit_word(self):
        """get_input should detect 'quit' as quit."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="quit"):
            result = screen.get_input()
        
        assert result.intent == "quit"
    
    def test_get_input_detects_back_lowercase(self):
        """get_input should detect 'b' as back."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="b"):
            result = screen.get_input()
        
        assert result.intent == "back"
        assert result.is_back is True
    
    def test_get_input_detects_back_uppercase(self):
        """get_input should detect 'B' as back."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="B"):
            result = screen.get_input()
        
        assert result.intent == "back"
    
    def test_get_input_detects_back_word(self):
        """get_input should detect 'back' as back."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="back"):
            result = screen.get_input()
        
        assert result.intent == "back"
    
    def test_get_input_preserves_raw_for_regular(self):
        """get_input should preserve raw input."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        
        screen = MainMenuScreen()
        with patch('builtins.input', return_value="123"):
            result = screen.get_input()
        
        assert result.raw == "123"
        assert result.intent is None


class TestConfirmQuit:
    """Tests for confirm_quit() function."""
    
    def test_confirm_quit_exists(self):
        """confirm_quit should be importable."""
        from kloudkompass.tui.screens import confirm_quit
        assert confirm_quit is not None
    
    def test_confirm_quit_y_returns_true(self):
        """confirm_quit should return True for 'y'."""
        from kloudkompass.tui.screens import confirm_quit
        
        with patch('builtins.input', return_value="y"):
            with patch('builtins.print'):
                result = confirm_quit()
        
        assert result is True
    
    def test_confirm_quit_yes_returns_true(self):
        """confirm_quit should return True for 'yes'."""
        from kloudkompass.tui.screens import confirm_quit
        
        with patch('builtins.input', return_value="yes"):
            with patch('builtins.print'):
                result = confirm_quit()
        
        assert result is True
    
    def test_confirm_quit_n_returns_false(self):
        """confirm_quit should return False for 'n'."""
        from kloudkompass.tui.screens import confirm_quit
        
        with patch('builtins.input', return_value="n"):
            with patch('builtins.print'):
                result = confirm_quit()
        
        assert result is False
    
    def test_confirm_quit_empty_returns_false(self):
        """confirm_quit should return False for empty input (default no)."""
        from kloudkompass.tui.screens import confirm_quit
        
        with patch('builtins.input', return_value=""):
            with patch('builtins.print'):
                result = confirm_quit()
        
        assert result is False


class TestMainMenuNoExit:
    """Tests that Exit is not a menu option (quit is via Q key, not a menu item)."""
    
    def test_menu_options_no_exit_action(self):
        """MENU_OPTIONS should not contain an 'exit' action."""
        from kloudkompass.tui.main_menu import MENU_OPTIONS
        
        for key, label, action in MENU_OPTIONS:
            assert action != "exit", "Exit should not be a menu option"
    
    def test_menu_option_zero_is_settings(self):
        """Key '0' should be assigned to Settings, not Exit."""
        from kloudkompass.tui.main_menu import MENU_OPTIONS
        
        zero_options = [(k, a) for k, _, a in MENU_OPTIONS if k == "0"]
        assert len(zero_options) == 1, "There should be exactly one key '0'"
        assert zero_options[0][1] == "settings", "Key '0' should be Settings"


class TestNavigationQuit:
    """Tests for quit navigation from any screen."""
    
    def test_main_menu_q_triggers_confirmation(self):
        """Main menu should show confirmation on Q."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        from kloudkompass.tui.navigation import reset_navigator
        
        reset_navigator()
        screen = MainMenuScreen()
        
        # Mock: Q pressed, then confirm N (don't quit)
        with patch('builtins.input', side_effect=["q", "n"]):
            with patch('builtins.print'):
                result = screen.handle_input()
        
        assert result is None  # Stayed on screen
    
    def test_main_menu_q_then_y_returns_exit(self):
        """Main menu should exit on Q -> Y."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        from kloudkompass.tui.navigation import reset_navigator
        
        reset_navigator()
        screen = MainMenuScreen()
        
        with patch('builtins.input', side_effect=["q", "y"]):
            with patch('builtins.print'):
                result = screen.handle_input()
        
        assert result == "exit"


class TestNavigationBack:
    """Tests for back navigation."""
    
    def test_back_at_root_triggers_confirmation(self):
        """Back at root should trigger quit confirmation."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        from kloudkompass.tui.navigation import reset_navigator
        
        reset_navigator()
        screen = MainMenuScreen()
        
        # Mock: B pressed, then confirm N (don't quit)
        with patch('builtins.input', side_effect=["b", "n"]):
            with patch('builtins.print'):
                result = screen.handle_input()
        
        assert result is None  # Stayed on screen
