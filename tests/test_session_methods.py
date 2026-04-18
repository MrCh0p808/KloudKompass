# tests/test_session_methods.py
# -------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 session with_* immutability tests (25 tests).

import pytest


class TestSessionWithProvider:
    """Tests for SessionState.with_provider()."""
    
    def test_returns_new_instance(self):
        from kloudkompass.tui.session import SessionState
        s1 = SessionState()
        s2 = s1.with_provider("aws")
        assert s1 is not s2
    
    def test_sets_provider(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_provider("aws")
        assert s.provider == "aws"
    
    def test_preserves_other_fields(self):
        from kloudkompass.tui.session import SessionState
        s1 = SessionState(debug_mode=True)
        s2 = s1.with_provider("aws")
        assert s2.debug_mode is True


class TestSessionWithDates:
    """Tests for SessionState.with_dates()."""
    
    def test_returns_new_instance(self):
        from kloudkompass.tui.session import SessionState
        s1 = SessionState()
        s2 = s1.with_dates("2026-01-01", "2026-01-31")
        assert s1 is not s2
    
    def test_sets_start_date(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_dates("2026-01-01", "2026-01-31")
        assert s.start_date == "2026-01-01"
    
    def test_sets_end_date(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_dates("2026-01-01", "2026-01-31")
        assert s.end_date == "2026-01-31"
    
    def test_preserves_provider(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState(provider="aws").with_dates("2026-01-01", "2026-01-31")
        assert s.provider == "aws"


class TestSessionWithBreakdown:
    """Tests for SessionState.with_breakdown()."""
    
    def test_sets_breakdown(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_breakdown("service")
        assert s.breakdown == "service"
    
    def test_returns_new_instance(self):
        from kloudkompass.tui.session import SessionState
        s1 = SessionState()
        s2 = s1.with_breakdown("service")
        assert s1 is not s2


class TestSessionWithThreshold:
    """Tests for SessionState.with_threshold()."""
    
    def test_sets_threshold(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_threshold(10.5)
        assert s.threshold == 10.5
    
    def test_zero_threshold(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_threshold(0.0)
        assert s.threshold == 0.0


class TestSessionWithProfile:
    """Tests for SessionState.with_profile()."""
    
    def test_sets_profile(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_profile("production")
        assert s.profile == "production"


class TestSessionWithRegion:
    """Tests for SessionState.with_region()."""
    
    def test_sets_region(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_region("us-east-1")
        assert s.region == "us-east-1"


class TestSessionWithOutputFormat:
    """Tests for SessionState.with_output_format()."""
    
    def test_sets_output_format(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_output_format("json")
        assert s.output_format == "json"


class TestSessionWithError:
    """Tests for SessionState.with_error()."""
    
    def test_sets_error(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_error("test error")
        assert s.last_error == "test error"


class TestSessionWithDebug:
    """Tests for SessionState.with_debug()."""
    
    def test_sets_debug(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState().with_debug(True)
        assert s.debug_mode is True
    
    def test_unsets_debug(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState(debug_mode=True).with_debug(False)
        assert s.debug_mode is False


class TestSessionResetCostOptions:
    """Tests for SessionState.reset_cost_options()."""
    
    def test_clears_dates(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState(start_date="2026-01-01", end_date="2026-01-31").reset_cost_options()
        assert s.start_date is None
        assert s.end_date is None
    
    def test_clears_breakdown(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState(breakdown="service").reset_cost_options()
        assert s.breakdown is None
    
    def test_clears_threshold(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState(threshold=10.0).reset_cost_options()
        assert s.threshold is None
    
    def test_preserves_provider(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState(provider="aws").reset_cost_options()
        assert s.provider == "aws"


class TestSessionToDict:
    """Tests for SessionState.to_dict()."""
    
    def test_returns_dict(self):
        from kloudkompass.tui.session import SessionState
        assert isinstance(SessionState().to_dict(), dict)
    
    def test_contains_all_keys(self):
        from kloudkompass.tui.session import SessionState
        d = SessionState().to_dict()
        assert "provider" in d
        assert "start_date" in d
        assert "breakdown" in d
        assert "threshold" in d
    
    def test_frozen_cannot_mutate(self):
        from kloudkompass.tui.session import SessionState
        s = SessionState()
        with pytest.raises(Exception):
            s.provider = "aws"
