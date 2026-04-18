# tests/test_lifecycle_model.py
# ------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 screen lifecycle tests (15 tests).

import pytest
from unittest.mock import patch, MagicMock


class TestScreenLifecycleMethods:
    """Tests for Screen lifecycle methods."""
    
    def test_screen_has_mount(self):
        """Screen should have mount method."""
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'mount')
    
    def test_screen_has_render(self):
        """Screen should have render method."""
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'render')
    
    def test_screen_has_unmount(self):
        """Screen should have unmount method."""
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'unmount')
    
    def test_screen_has_display(self):
        """Screen should have display method."""
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'display')
    
    def test_screen_has_run(self):
        """Screen should have run method."""
        from kloudkompass.tui.screens import Screen
        assert hasattr(Screen, 'run')


class TestMountedGuard:
    """Tests for _mounted guard preventing duplicate mount."""
    
    def test_screen_has_mounted_flag(self):
        """Screen should have _mounted flag."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        screen = MainMenuScreen()
        assert hasattr(screen, '_mounted')
    
    def test_mounted_starts_false(self):
        """_mounted should start as False."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        screen = MainMenuScreen()
        assert screen._mounted is False
    
    def test_mount_sets_mounted_true(self):
        """mount() should set _mounted to True."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        screen = MainMenuScreen()
        with patch('builtins.print'):
            screen.mount()
        assert screen._mounted is True
    
    def test_mount_only_runs_once(self):
        """mount() should not run twice."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        screen = MainMenuScreen()
        
        call_count = 0
        original_print_header = screen.print_header
        def counting_print_header():
            nonlocal call_count
            call_count += 1
            original_print_header()
        
        screen.print_header = counting_print_header
        
        with patch('builtins.print'):
            screen.mount()
            screen.mount()  # Should not call print_header again
        
        assert call_count == 1


class TestDisplayCallsLifecycle:
    """Tests that display() correctly calls lifecycle."""
    
    def test_display_calls_mount(self):
        """display() should call mount()."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        screen = MainMenuScreen()
        
        mount_called = False
        original_mount = screen.mount
        def mock_mount():
            nonlocal mount_called
            mount_called = True
            original_mount()
        
        screen.mount = mock_mount
        
        with patch('builtins.print'):
            screen.display()
        
        assert mount_called
    
    def test_display_calls_render(self):
        """display() should call render()."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        screen = MainMenuScreen()
        screen._mounted = True  # Skip mount
        
        render_called = False
        original_render = screen.render
        def mock_render():
            nonlocal render_called
            render_called = True
            original_render()
        
        screen.render = mock_render
        
        with patch('builtins.print'):
            screen.display()
        
        assert render_called


class TestPrintHeaderBehavior:
    """Tests for print_header behavior."""
    
    def test_print_header_clears_screen(self):
        """print_header should clear screen first."""
        from kloudkompass.tui.screens import Screen
        import inspect
        source = inspect.getsource(Screen.print_header)
        # Check for escape sequence that clears screen
        assert '\\033[2J' in source or 'clear' in source.lower()
    
    def test_print_header_prints_title(self):
        """print_header should print screen title."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        from kloudkompass.tui.screens import BRAND_TITLE
        
        screen = MainMenuScreen()
        output = []
        
        with patch('builtins.print', side_effect=lambda *a, **k: output.append(str(a))):
            screen.print_header()
        
        # Join all output and check for title
        all_output = ' '.join(output)
        assert BRAND_TITLE in all_output or 'Kloud Kompass' in all_output
