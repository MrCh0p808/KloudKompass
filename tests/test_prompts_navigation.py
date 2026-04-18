# tests/test_prompts_navigation.py
# ---------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 prompts navigation tests (15 tests).

import pytest
from unittest.mock import patch


class TestCheckNavigation:
    """Tests for _check_navigation helper."""
    
    def test_check_navigation_exists(self):
        """_check_navigation should exist."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation is not None
    
    def test_q_returns_quit(self):
        """'q' should return 'quit'."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('q') == 'quit'
    
    def test_Q_returns_quit(self):
        """'Q' should return 'quit'."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('Q') == 'quit'
    
    def test_quit_returns_quit(self):
        """'quit' should return 'quit'."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('quit') == 'quit'
    
    def test_b_returns_back(self):
        """'b' should return 'back'."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('b') == 'back'
    
    def test_B_returns_back(self):
        """'B' should return 'back'."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('B') == 'back'
    
    def test_back_returns_back(self):
        """'back' should return 'back'."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('back') == 'back'
    
    def test_number_returns_none(self):
        """Number input should return None."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('1') is None
        assert _check_navigation('42') is None
    
    def test_text_returns_none(self):
        """Regular text should return None."""
        from kloudkompass.tui.prompts import _check_navigation
        assert _check_navigation('aws') is None
        assert _check_navigation('hello') is None


class TestSelectProviderNavigation:
    """Tests for select_provider navigation handling."""
    
    def test_select_provider_handles_q(self):
        """select_provider should handle 'q' as quit."""
        from kloudkompass.tui.prompts import select_provider
        
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print'):
                result, action = select_provider()
        
        assert action == 'quit'
    
    def test_select_provider_handles_b(self):
        """select_provider should handle 'b' as back."""
        from kloudkompass.tui.prompts import select_provider
        
        with patch('builtins.input', return_value='b'):
            with patch('builtins.print'):
                result, action = select_provider()
        
        assert action == 'back'
    
    def test_select_provider_handles_zero(self):
        """select_provider should handle '0' as back."""
        from kloudkompass.tui.prompts import select_provider
        
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print'):
                result, action = select_provider()
        
        assert action == 'back'


class TestSelectBreakdownNavigation:
    """Tests for select_breakdown navigation."""
    
    def test_select_breakdown_handles_q(self):
        """select_breakdown should handle 'q' as quit."""
        from kloudkompass.tui.prompts import select_breakdown
        
        with patch('builtins.input', return_value='q'):
            with patch('builtins.print'):
                result, action = select_breakdown()
        
        assert action == 'quit'
    
    def test_select_breakdown_handles_zero(self):
        """select_breakdown should handle '0' as back."""
        from kloudkompass.tui.prompts import select_breakdown
        
        with patch('builtins.input', return_value='0'):
            with patch('builtins.print'):
                result, action = select_breakdown()
        
        assert action == 'back'
