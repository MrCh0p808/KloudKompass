# tests/test_navigator_advanced.py
# ----------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 navigator advanced tests (20 tests).

import pytest
from unittest.mock import MagicMock


class TestNavigatorPushPop:
    """Tests for push/pop sequencing."""
    
    def test_push_increases_depth(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        screen = MagicMock()
        nav.push(screen)
        assert nav.depth == 1
    
    def test_push_two_depth_two(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.push(MagicMock())
        nav.push(MagicMock())
        assert nav.depth == 2
    
    def test_pop_decreases_depth(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.push(MagicMock())
        nav.push(MagicMock())
        nav.pop()
        assert nav.depth == 1
    
    def test_pop_returns_previous(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        s1 = MagicMock()
        s2 = MagicMock()
        nav.push(s1)
        nav.push(s2)
        result = nav.pop()
        assert result is s1
    
    def test_pop_empty_returns_none(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        assert nav.pop() is None
    
    def test_current_returns_topmost(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        s1 = MagicMock()
        s2 = MagicMock()
        nav.push(s1)
        nav.push(s2)
        assert nav.current() is s2
    
    def test_current_empty_returns_none(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        assert nav.current() is None


class TestNavigatorClear:
    """Tests for clear and reset_to."""
    
    def test_clear_empties_stack(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.push(MagicMock())
        nav.push(MagicMock())
        nav.clear()
        assert nav.depth == 0
    
    def test_reset_to_sets_root(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.push(MagicMock())
        nav.push(MagicMock())
        root = MagicMock()
        nav.reset_to(root)
        assert nav.depth == 1
        assert nav.current() is root
    
    def test_clear_then_current_none(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.push(MagicMock())
        nav.clear()
        assert nav.current() is None


class TestNavigatorExit:
    """Tests for exit request."""
    
    def test_should_exit_default_false(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        assert nav.should_exit() is False
    
    def test_request_exit_sets_flag(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.request_exit()
        assert nav.should_exit() is True


class TestNavigatorCanGoBack:
    """Tests for can_go_back property."""
    
    def test_empty_cannot_go_back(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        assert nav.can_go_back is False
    
    def test_one_screen_cannot_go_back(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.push(MagicMock())
        assert nav.can_go_back is False
    
    def test_two_screens_can_go_back(self):
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        nav.push(MagicMock())
        nav.push(MagicMock())
        assert nav.can_go_back is True


class TestNavigatorSingleton:
    """Tests for global navigator instance."""
    
    def test_get_navigator_returns_navigator(self):
        from kloudkompass.tui.navigation import get_navigator, Navigator
        nav = get_navigator()
        assert isinstance(nav, Navigator)
    
    def test_get_navigator_same_instance(self):
        from kloudkompass.tui.navigation import get_navigator
        n1 = get_navigator()
        n2 = get_navigator()
        assert n1 is n2
    
    def test_reset_navigator_creates_new(self):
        from kloudkompass.tui.navigation import get_navigator, reset_navigator
        n1 = get_navigator()
        n2 = reset_navigator()
        assert n1 is not n2
