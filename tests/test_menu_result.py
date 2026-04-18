# tests/test_menu_result.py
# --------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Tests for MenuResult frozen dataclass per Master Brief navigation contract.

import pytest

from kloudkompass.tui.menu_result import MenuResult, BACK, EXIT, result_next


class TestMenuResultCreation:
    """Tests for MenuResult creation and validation."""
    
    def test_create_next_action(self):
        """Should create MenuResult with next action."""
        result = MenuResult(value="test", action="next")
        
        assert result.value == "test"
        assert result.action == "next"
    
    def test_create_back_action(self):
        """Should create MenuResult with back action."""
        result = MenuResult(value=None, action="back")
        
        assert result.value is None
        assert result.action == "back"
    
    def test_create_exit_action(self):
        """Should create MenuResult with exit action."""
        result = MenuResult(value=None, action="exit")
        
        assert result.action == "exit"
    
    def test_invalid_action_raises(self):
        """Should raise ValueError for invalid action."""
        with pytest.raises(ValueError) as exc_info:
            MenuResult(value=None, action="invalid")
        
        assert "invalid" in str(exc_info.value).lower()


class TestMenuResultFrozen:
    """Tests for frozen dataclass enforcement."""
    
    def test_cannot_modify_value(self):
        """Should not allow modifying value after creation."""
        result = MenuResult(value="original", action="next")
        
        with pytest.raises(AttributeError):
            result.value = "modified"
    
    def test_cannot_modify_action(self):
        """Should not allow modifying action after creation."""
        result = MenuResult(value=None, action="next")
        
        with pytest.raises(AttributeError):
            result.action = "back"


class TestMenuResultProperties:
    """Tests for convenience properties."""
    
    def test_is_next(self):
        """Should identify next action."""
        result = MenuResult(value="x", action="next")
        
        assert result.is_next is True
        assert result.is_back is False
        assert result.is_exit is False
    
    def test_is_back(self):
        """Should identify back action."""
        result = MenuResult(value=None, action="back")
        
        assert result.is_back is True
        assert result.is_next is False
        assert result.is_exit is False
    
    def test_is_exit(self):
        """Should identify exit action."""
        result = MenuResult(value=None, action="exit")
        
        assert result.is_exit is True
        assert result.is_next is False
        assert result.is_back is False


class TestMenuResultHelpers:
    """Tests for helper constants and functions."""
    
    def test_back_constant(self):
        """BACK should be pre-built result."""
        assert BACK.action == "back"
        assert BACK.value is None
    
    def test_exit_constant(self):
        """EXIT should be pre-built result."""
        assert EXIT.action == "exit"
        assert EXIT.value is None
    
    def test_result_next_function(self):
        """result_next should create next action with value."""
        result = result_next("my_value")
        
        assert result.action == "next"
        assert result.value == "my_value"


class TestMenuResultEquality:
    """Tests for equality comparison."""
    
    def test_equal_results(self):
        """Should be equal with same value and action."""
        r1 = MenuResult(value="x", action="next")
        r2 = MenuResult(value="x", action="next")
        
        assert r1 == r2
    
    def test_different_value_not_equal(self):
        """Should not be equal with different values."""
        r1 = MenuResult(value="x", action="next")
        r2 = MenuResult(value="y", action="next")
        
        assert r1 != r2
    
    def test_different_action_not_equal(self):
        """Should not be equal with different actions."""
        r1 = MenuResult(value=None, action="back")
        r2 = MenuResult(value=None, action="exit")
        
        assert r1 != r2
