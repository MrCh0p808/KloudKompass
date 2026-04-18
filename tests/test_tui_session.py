# tests/test_tui_session.py
# --------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Tests the TUI session management. Updated to use immutable pattern
# per Master Brief session immutability requirement.

import pytest

from kloudkompass.tui.session import SessionState, get_session, reset_session, update_session


class TestSessionState:
    """Tests for SessionState frozen dataclass."""
    
    def test_default_values(self):
        """Session should have None defaults."""
        session = SessionState()
        assert session.provider is None
        assert session.start_date is None
        assert session.end_date is None
        assert session.breakdown is None
    
    def test_create_with_provider(self):
        """Should create session with provider."""
        session = SessionState(provider="aws")
        assert session.provider == "aws"
    
    def test_create_with_dates(self):
        """Should create session with date range."""
        session = SessionState(start_date="2024-01-01", end_date="2024-02-01")
        assert session.start_date == "2024-01-01"
        assert session.end_date == "2024-02-01"
    
    def test_reset_cost_options(self):
        """reset_cost_options should return new session with cleared cost fields."""
        session = SessionState(
            provider="aws",
            start_date="2024-01-01",
            end_date="2024-02-01",
            breakdown="service",
            threshold=5.0,
        )
        
        reset = session.reset_cost_options()
        
        # Original unchanged
        assert session.start_date == "2024-01-01"
        # Reset has cost options cleared but provider preserved
        assert reset.provider == "aws"
        assert reset.start_date is None
        assert reset.end_date is None
        assert reset.breakdown is None
        assert reset.threshold is None
    
    def test_reset_all_returns_new_session(self):
        """reset_all should return new session with defaults."""
        session = SessionState(
            provider="aws",
            profile="prod",
            start_date="2024-01-01",
            debug_mode=True,
        )
        
        reset = session.reset_all()
        
        assert reset.provider is None
        assert reset.profile is None
        assert reset.start_date is None
        # debug_mode is preserved
        assert reset.debug_mode is True
    
    def test_to_dict(self):
        """to_dict should return serializable dictionary."""
        session = SessionState(provider="aws", start_date="2024-01-01")
        
        d = session.to_dict()
        
        assert isinstance(d, dict)
        assert d["provider"] == "aws"
        assert d["start_date"] == "2024-01-01"


class TestSessionSingleton:
    """Tests for session singleton pattern."""
    
    def test_get_session_returns_same_instance(self):
        """get_session should return the same instance."""
        reset_session()
        s1 = get_session()
        s2 = get_session()
        assert s1 is s2
    
    def test_reset_session_creates_new_instance(self):
        """reset_session should create a fresh session."""
        # Set up initial state
        initial = SessionState(provider="aws")
        update_session(initial)
        
        # Reset should create new session
        s2 = reset_session()
        
        assert s2.provider is None
        assert get_session() is s2
