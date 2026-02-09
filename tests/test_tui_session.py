# tests/test_tui_session.py
# --------------------------
# Tests the TUI session management. These tests verify that session
# state persists correctly across screen navigation.

import pytest

from bashcloud.tui.session import SessionState, get_session, reset_session


class TestSessionState:
    """Tests for SessionState dataclass."""
    
    def test_default_values(self):
        """Session should have None defaults."""
        session = SessionState()
        assert session.provider is None
        assert session.start_date is None
        assert session.end_date is None
        assert session.breakdown is None
    
    def test_store_provider(self):
        """Should store provider selection."""
        session = SessionState()
        session.provider = "aws"
        assert session.provider == "aws"
    
    def test_store_dates(self):
        """Should store date range."""
        session = SessionState()
        session.start_date = "2024-01-01"
        session.end_date = "2024-02-01"
        assert session.start_date == "2024-01-01"
        assert session.end_date == "2024-02-01"
    
    def test_reset_cost_options(self):
        """reset_cost_options should clear cost-related fields."""
        session = SessionState()
        session.start_date = "2024-01-01"
        session.end_date = "2024-02-01"
        session.breakdown = "service"
        session.threshold = 5.0
        
        session.reset_cost_options()
        
        assert session.start_date is None
        assert session.end_date is None
        assert session.breakdown is None
        assert session.threshold is None
    
    def test_reset_all_clears_everything(self):
        """reset_all should clear all session state."""
        session = SessionState()
        session.provider = "aws"
        session.profile = "prod"
        session.start_date = "2024-01-01"
        session.data["custom"] = "value"
        
        session.reset_all()
        
        assert session.provider is None
        assert session.profile is None
        assert session.start_date is None
        assert len(session.data) == 0
    
    def test_to_dict(self):
        """to_dict should return serializable dictionary."""
        session = SessionState()
        session.provider = "aws"
        session.start_date = "2024-01-01"
        
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
        s1 = get_session()
        s1.provider = "aws"
        
        s2 = reset_session()
        
        assert s2.provider is None
        assert get_session() is s2
