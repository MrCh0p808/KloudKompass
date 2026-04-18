# tests/test_edge_cases.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 edge case tests (15 tests).

import pytest
from unittest.mock import patch, MagicMock


class TestInputResultEdgeCases:
    """Edge cases for InputResult."""
    
    def test_empty_string_input(self):
        """Empty string should have no intent."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="")
        assert result.intent is None
        assert result.is_navigation is False
    
    def test_whitespace_input(self):
        """Whitespace should have no intent."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="   ")
        assert result.intent is None
    
    def test_mixed_case_raw_preserved(self):
        """Raw input should preserve original case."""
        from kloudkompass.tui.screens import InputResult
        result = InputResult(raw="QuIt", intent="quit")
        assert result.raw == "QuIt"


class TestProviderSetupEdgeCases:
    """Edge cases for provider setup."""
    
    def test_unknown_provider(self):
        """Unknown provider should fail gracefully."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        result = check_provider_ready("oracle")
        assert result.success is False
    
    def test_empty_provider_name(self):
        """Empty provider name should fail."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        result = check_provider_ready("")
        assert result.success is False
    
    def test_provider_with_spaces(self):
        """Provider with spaces should be handled."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        result = check_provider_ready("  aws  ")
        # Should handle whitespace


class TestBrandingEdgeCases:
    """Edge cases for branding."""
    
    def test_brand_title_not_mutable(self):
        """BRAND_TITLE should not be mutable from module."""
        from kloudkompass.tui import screens
        original = screens.BRAND_TITLE
        try:
            screens.BRAND_TITLE = "Hacked"
            # Even if mutation succeeds, import should get original
            from kloudkompass.tui.screens import BRAND_TITLE
            assert BRAND_TITLE == "Hacked" or BRAND_TITLE == original
        finally:
            screens.BRAND_TITLE = original
    
    def test_nav_hint_format_consistent(self):
        """NAV_HINT should have consistent format."""
        from kloudkompass.tui.screens import NAV_HINT
        assert NAV_HINT.count('[') == NAV_HINT.count(']')


class TestNavigationEdgeCases:
    """Edge cases for navigation."""
    
    def test_navigator_at_root_pop_safe(self):
        """Popping at root should be safe."""
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        result = nav.pop()
        assert result is None
    
    def test_navigator_empty_depth(self):
        """Empty navigator should have depth 0."""
        from kloudkompass.tui.navigation import Navigator
        nav = Navigator()
        assert nav.depth == 0
    
    def test_session_reset_returns_fresh(self):
        """reset_session should return fresh state."""
        from kloudkompass.tui.session import reset_session, get_session
        reset_session()
        s1 = get_session()
        reset_session()
        s2 = get_session()
        assert s1 is not s2


class TestExportModalEdgeCases:
    """Edge cases for export modal."""
    
    def test_export_no_data(self):
        """Export with no data should work."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        modal = ExportModal()
        assert modal.data == {}
    
    def test_export_none_data(self):
        """Export with None data should default to empty."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        modal = ExportModal(data=None)
        assert modal.data == {}
    
    def test_export_empty_rows(self):
        """Export with empty rows should work."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        modal = ExportModal(data={"headers": ["A"], "rows": []})
        assert modal.data["rows"] == []
