# tests/test_analytics_widgets.py
# -------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Wave 7.2 analytics UI widget tests.

import pytest
from textual.app import App


class TestCostChart:
    """Tests for CostChart sparkline widget."""

    def test_cost_chart_import(self):
        """CostChart should import without errors."""
        from kloudkompass.dashboard.widgets import CostChart
        assert CostChart is not None

    def test_cost_chart_has_load_data(self):
        """CostChart should have load_data method."""
        from kloudkompass.dashboard.widgets import CostChart
        assert hasattr(CostChart, "load_data")

    def test_cost_chart_has_clear_data(self):
        """CostChart should have clear_data method."""
        from kloudkompass.dashboard.widgets import CostChart
        assert hasattr(CostChart, "clear_data")


class TestResourceSummary:
    """Tests for ResourceSummary bar."""

    def test_resource_summary_import(self):
        """ResourceSummary should import without errors."""
        from kloudkompass.dashboard.widgets import ResourceSummary
        assert ResourceSummary is not None

    def test_resource_summary_set_counts(self):
        """ResourceSummary should have set_counts method."""
        from kloudkompass.dashboard.widgets import ResourceSummary
        assert hasattr(ResourceSummary, "set_counts")


class TestSecurityScoreGauge:
    """Tests for SecurityScoreGauge."""

    def test_security_score_import(self):
        """SecurityScoreGauge should import without errors."""
        from kloudkompass.dashboard.widgets import SecurityScoreGauge
        assert SecurityScoreGauge is not None

    def test_security_score_set_score(self):
        """SecurityScoreGauge should have set_score method."""
        from kloudkompass.dashboard.widgets import SecurityScoreGauge
        assert hasattr(SecurityScoreGauge, "set_score")

    def test_security_score_clamp(self):
        """Security score should clamp negative values to 0."""
        from kloudkompass.dashboard.widgets import SecurityScoreGauge
        
        gauge = SecurityScoreGauge()
        gauge.set_score(-15, 0)
        assert gauge._score == 0
        
        gauge.set_score(150, 0)
        assert gauge._score == 100
        
        gauge.set_score(85, 0)
        assert gauge._score == 85
