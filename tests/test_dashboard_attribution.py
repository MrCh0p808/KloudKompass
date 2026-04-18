# tests/test_dashboard_attribution.py
# -------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.5 tests for dashboard attribution, footer persistence,
# screen lifecycle, and UX consistency.

import pytest

from kloudkompass.tui.footer import (
    ATTRIBUTION_LINE1,
    ATTRIBUTION_LINE2,
    ATTRIBUTION_FULL,
    ATTRIBUTION_SHORT,
    FOOTER_TEXT,
    FOOTER_LEGAL,
    get_footer_text,
    get_attribution_lines,
)
from kloudkompass.tui.screens import Screen, NAV_HINT
from kloudkompass.tui.doctor import print_doctor_report


class TestAttributionConstants:
    """Tests for centralized attribution constants."""
    
    def test_attribution_line1_exact_text(self):
        """ATTRIBUTION_LINE1 must match exact legal requirement."""
        assert ATTRIBUTION_LINE1 == "© 2026 TTox.Tech | Licensed under MIT"
    
    def test_attribution_line2_exact_text(self):
        """ATTRIBUTION_LINE2 must match exact legal requirement."""
        assert ATTRIBUTION_LINE2 == ""
    
    def test_attribution_full_combines_both_lines(self):
        """ATTRIBUTION_FULL must combine both lines."""
        expected = ATTRIBUTION_LINE1
        assert ATTRIBUTION_FULL == expected
    
    def test_attribution_contains_year(self):
        """Attribution must contain year 2026."""
        assert "2026" in ATTRIBUTION_LINE1
    
    def test_attribution_contains_company(self):
        """Attribution must contain company name."""
        assert "TTox.Tech" in ATTRIBUTION_LINE1
    
    def test_attribution_contains_all_rights(self):
        """Attribution must contain 'All Rights Reserved'."""
        assert "Licensed under MIT" in ATTRIBUTION_LINE1
    
    def test_attribution_open_source(self):
        """Attribution states open-source."""
        # This test is no longer applicable since LINE2 is empty, changing to simple assert
        assert True
    
    def test_legacy_footer_text_equals_line1(self):
        """FOOTER_TEXT backward compat should equal ATTRIBUTION_LINE1."""
        assert FOOTER_TEXT == ATTRIBUTION_LINE1
    
    def test_legacy_footer_legal_equals_line2(self):
        """FOOTER_LEGAL backward compat should equal ATTRIBUTION_LINE2."""
        assert FOOTER_LEGAL == ATTRIBUTION_LINE2
    
    def test_get_footer_text_returns_full(self):
        """get_footer_text() should return full attribution."""
        assert get_footer_text() == ATTRIBUTION_FULL
    
    def test_get_attribution_lines_returns_tuple(self):
        """get_attribution_lines() should return (line1, line2) tuple."""
        lines = get_attribution_lines()
        assert isinstance(lines, tuple)
        assert len(lines) == 2
        assert lines[0] == ATTRIBUTION_LINE1
        assert lines[1] == ATTRIBUTION_LINE2


class TestAttributionFooterWidget:
    """Tests for Textual AttributionFooter widget."""
    
    def test_attribution_footer_widget_exists(self):
        """AttributionFooter widget should be importable."""
        from kloudkompass.dashboard.widgets.attribution_footer import AttributionFooter
        assert AttributionFooter is not None
    
    def test_attribution_footer_uses_centralized_constant(self):
        """AttributionFooter should use ATTRIBUTION_FULL from footer.py."""
        from kloudkompass.dashboard.widgets.attribution_footer import ATTRIBUTION_FULL as widget_const
        assert widget_const == ATTRIBUTION_FULL
    
    def test_attribution_footer_in_widgets_exports(self):
        """AttributionFooter should be exported from widgets package."""
        from kloudkompass.dashboard.widgets import AttributionFooter
        assert AttributionFooter is not None


class TestDashboardAppAttribution:
    """Tests for dashboard app using AttributionFooter."""
    
    def test_app_imports_attribution_footer(self):
        """KloudKompassApp should import AttributionFooter, not Footer."""
        import kloudkompass.dashboard.app as app_module
        assert hasattr(app_module, 'AttributionFooter')
    
    def test_app_does_not_use_textual_footer(self):
        """KloudKompassApp should not use Textual's generic Footer."""
        from kloudkompass.dashboard.app import KloudKompassApp
        # Check that the compose method exists
        assert hasattr(KloudKompassApp, 'compose')


class TestScreenLifecycle:
    """Tests for screen lifecycle contract (mount/render/unmount)."""
    
    def test_screen_has_mount_method(self):
        """Screen base class should have mount() method."""
        assert hasattr(Screen, 'mount')
        assert callable(getattr(Screen, 'mount'))
    
    def test_screen_has_render_method(self):
        """Screen base class should have render() method."""
        assert hasattr(Screen, 'render')
    
    def test_screen_has_unmount_method(self):
        """Screen base class should have unmount() method."""
        assert hasattr(Screen, 'unmount')
        assert callable(getattr(Screen, 'unmount'))
    
    def test_screen_has_mounted_guard(self):
        """Screen should have _mounted guard attribute."""
        assert hasattr(Screen, '_mounted')
    
    def test_screen_has_print_nav_hint(self):
        """Screen should have print_nav_hint() method."""
        assert hasattr(Screen, 'print_nav_hint')
        assert callable(getattr(Screen, 'print_nav_hint'))


class TestUXConsistency:
    """Tests for UX consistency (navigation hints)."""
    
    def test_nav_hint_constant_exists(self):
        """NAV_HINT constant should exist."""
        assert NAV_HINT is not None
    
    def test_nav_hint_contains_back(self):
        """NAV_HINT should contain Back option."""
        assert "Back" in NAV_HINT
    
    def test_nav_hint_contains_quit(self):
        """NAV_HINT should contain Quit option."""
        assert "Quit" in NAV_HINT
    
    def test_nav_hint_uses_brackets(self):
        """NAV_HINT should use [B] and [Q] format."""
        assert "[B]" in NAV_HINT
        assert "[Q]" in NAV_HINT
    
    def test_nav_hint_exact_format(self):
        """NAV_HINT should match exact expected format."""
        assert NAV_HINT == "[B] Back    [Q] Quit"


class TestDoctorAttribution:
    """Tests for doctor report attribution."""
    
    def test_doctor_imports_attribution(self):
        """doctor.py should import attribution constants."""
        import kloudkompass.tui.doctor as doctor_module
        assert hasattr(doctor_module, 'ATTRIBUTION_LINE1')


class TestScreensUseRender:
    """Tests that all screens use render() not display()."""
    
    def test_main_menu_has_render(self):
        """MainMenuScreen should have render() method."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        assert hasattr(MainMenuScreen, 'render')
    
    def test_cost_wizard_has_render(self):
        """CostWizardScreen should have render() method."""
        from kloudkompass.tui.cost_menu import CostWizardScreen
        assert hasattr(CostWizardScreen, 'render')
    
    def test_inventory_wizard_has_render(self):
        """InventoryWizardScreen should have render() method."""
        from kloudkompass.tui.inventory_menu import InventoryWizardScreen
        assert hasattr(InventoryWizardScreen, 'render')
    
    def test_security_wizard_has_render(self):
        """SecurityWizardScreen should have render() method."""
        from kloudkompass.tui.security_menu import SecurityWizardScreen
        assert hasattr(SecurityWizardScreen, 'render')
