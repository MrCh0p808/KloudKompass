# tests/test_session_immutable.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Tests for immutable SessionState per Master Brief.

import pytest

from kloudkompass.tui.session import SessionState, get_session, update_session, reset_session


class TestSessionStateFrozen:
    """Tests for frozen dataclass enforcement."""
    
    def test_cannot_modify_provider(self):
        """Should not allow modifying provider after creation."""
        session = SessionState(provider="aws")
        
        with pytest.raises(AttributeError):
            session.provider = "azure"
    
    def test_cannot_modify_dates(self):
        """Should not allow modifying dates after creation."""
        session = SessionState(start_date="2024-01-01")
        
        with pytest.raises(AttributeError):
            session.start_date = "2024-02-01"
    
    def test_cannot_modify_breakdown(self):
        """Should not allow modifying breakdown after creation."""
        session = SessionState(breakdown="service")
        
        with pytest.raises(AttributeError):
            session.breakdown = "daily"


class TestSessionStateWithMethods:
    """Tests for with_* immutable update methods."""
    
    def test_with_provider_returns_new_instance(self):
        """with_provider should return new session, not modify original."""
        original = SessionState(provider="aws")
        updated = original.with_provider("azure")
        
        assert original.provider == "aws"
        assert updated.provider == "azure"
        assert original is not updated
    
    def test_with_dates_returns_new_instance(self):
        """with_dates should return new session."""
        original = SessionState()
        updated = original.with_dates("2024-01-01", "2024-02-01")
        
        assert original.start_date is None
        assert updated.start_date == "2024-01-01"
        assert updated.end_date == "2024-02-01"
        assert original is not updated
    
    def test_with_breakdown_returns_new_instance(self):
        """with_breakdown should return new session."""
        original = SessionState()
        updated = original.with_breakdown("service")
        
        assert original.breakdown is None
        assert updated.breakdown == "service"
    
    def test_with_threshold_returns_new_instance(self):
        """with_threshold should return new session."""
        original = SessionState()
        updated = original.with_threshold(5.0)
        
        assert original.threshold is None
        assert updated.threshold == 5.0
    
    def test_with_output_format_returns_new_instance(self):
        """with_output_format should return new session."""
        original = SessionState()
        updated = original.with_output_format("json")
        
        assert original.output_format is None
        assert updated.output_format == "json"
    
    def test_chained_updates(self):
        """Should support chained updates."""
        session = (
            SessionState()
            .with_provider("aws")
            .with_dates("2024-01-01", "2024-02-01")
            .with_breakdown("service")
            .with_threshold(1.0)
        )
        
        assert session.provider == "aws"
        assert session.start_date == "2024-01-01"
        assert session.end_date == "2024-02-01"
        assert session.breakdown == "service"
        assert session.threshold == 1.0


class TestSessionStateReset:
    """Tests for reset methods."""
    
    def test_reset_cost_options_returns_new_instance(self):
        """reset_cost_options should return new session with cleared cost data."""
        original = SessionState(
            provider="aws",
            start_date="2024-01-01",
            end_date="2024-02-01",
            breakdown="service",
            threshold=5.0,
        )
        
        reset = original.reset_cost_options()
        
        # Provider preserved
        assert reset.provider == "aws"
        # Cost options cleared
        assert reset.start_date is None
        assert reset.end_date is None
        assert reset.breakdown is None
        assert reset.threshold is None
        # Original unchanged
        assert original.start_date == "2024-01-01"
    
    def test_reset_all_returns_fresh_session(self):
        """reset_all should return fresh session."""
        original = SessionState(
            provider="aws",
            start_date="2024-01-01",
            debug_mode=True,
        )
        
        reset = original.reset_all()
        
        # All cleared except debug_mode
        assert reset.provider is None
        assert reset.start_date is None
        assert reset.debug_mode is True  # Preserved


class TestSessionStateGlobal:
    """Tests for global session management."""
    
    def test_get_session_returns_singleton(self):
        """get_session should return same instance."""
        reset_session()  # Start fresh
        
        s1 = get_session()
        s2 = get_session()
        
        assert s1 is s2
    
    def test_update_session_replaces_global(self):
        """update_session should replace the global instance."""
        reset_session()
        
        original = get_session()
        new_session = original.with_provider("azure")
        update_session(new_session)
        
        current = get_session()
        
        assert current.provider == "azure"
        assert current is new_session
    
    def test_reset_session_creates_fresh(self):
        """reset_session should create fresh session."""
        update_session(SessionState(provider="aws"))
        
        reset = reset_session()
        
        assert reset.provider is None


class TestSessionStateToDict:
    """Tests for serialization."""
    
    def test_to_dict(self):
        """Should convert to dictionary."""
        session = SessionState(
            provider="aws",
            start_date="2024-01-01",
            end_date="2024-02-01",
        )
        
        d = session.to_dict()
        
        assert d["provider"] == "aws"
        assert d["start_date"] == "2024-01-01"
        assert d["end_date"] == "2024-02-01"
