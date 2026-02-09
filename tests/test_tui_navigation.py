# tests/test_tui_navigation.py
# -----------------------------
# Tests the navigation controller. These tests verify that the
# stack-based navigation works correctly for back/forward flow.

import pytest

from bashcloud.tui.navigation import Navigator, get_navigator, reset_navigator
from bashcloud.tui.screens import Screen


class MockScreen(Screen):
    """Mock screen for testing."""
    
    def __init__(self, name: str = "mock"):
        super().__init__()
        self.name = name
    
    def display(self):
        pass
    
    def handle_input(self):
        return None


class TestNavigator:
    """Tests for Navigator class."""
    
    def test_empty_navigator(self):
        """New navigator should be empty."""
        nav = Navigator()
        assert nav.depth == 0
        assert nav.current() is None
    
    def test_push_screen(self):
        """push should add screen to stack."""
        nav = Navigator()
        screen = MockScreen("test")
        
        nav.push(screen)
        
        assert nav.depth == 1
        assert nav.current() is screen
    
    def test_pop_screen(self):
        """pop should remove and return previous screen."""
        nav = Navigator()
        screen1 = MockScreen("first")
        screen2 = MockScreen("second")
        
        nav.push(screen1)
        nav.push(screen2)
        
        result = nav.pop()
        
        assert nav.depth == 1
        assert result is screen1
        assert nav.current() is screen1
    
    def test_pop_empty_stack(self):
        """pop on empty stack should return None."""
        nav = Navigator()
        result = nav.pop()
        assert result is None
    
    def test_can_go_back(self):
        """can_go_back should be True when depth > 1."""
        nav = Navigator()
        assert nav.can_go_back is False
        
        nav.push(MockScreen())
        assert nav.can_go_back is False
        
        nav.push(MockScreen())
        assert nav.can_go_back is True
    
    def test_clear(self):
        """clear should empty the stack."""
        nav = Navigator()
        nav.push(MockScreen())
        nav.push(MockScreen())
        
        nav.clear()
        
        assert nav.depth == 0
    
    def test_reset_to(self):
        """reset_to should clear and set new root."""
        nav = Navigator()
        nav.push(MockScreen("old1"))
        nav.push(MockScreen("old2"))
        
        new_root = MockScreen("new")
        nav.reset_to(new_root)
        
        assert nav.depth == 1
        assert nav.current() is new_root
    
    def test_request_exit(self):
        """request_exit should signal exit."""
        nav = Navigator()
        assert nav.should_exit() is False
        
        nav.request_exit()
        
        assert nav.should_exit() is True


class TestNavigatorSingleton:
    """Tests for navigator singleton."""
    
    def test_get_navigator_returns_same_instance(self):
        """get_navigator should return the same instance."""
        reset_navigator()
        n1 = get_navigator()
        n2 = get_navigator()
        assert n1 is n2
    
    def test_reset_navigator_creates_new_instance(self):
        """reset_navigator should create fresh navigator."""
        n1 = get_navigator()
        n1.push(MockScreen())
        
        n2 = reset_navigator()
        
        assert n2.depth == 0
        assert get_navigator() is n2
