# tests/test_branding_consistency.py
# -----------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 branding consistency tests.

import pytest
import inspect


class TestBrandingConstants:
    """Tests for centralized branding constants."""
    
    def test_brand_title_exists(self):
        """BRAND_TITLE should be defined."""
        from kloudkompass.tui.screens import BRAND_TITLE
        assert BRAND_TITLE is not None
    
    def test_brand_title_exact_value(self):
        """BRAND_TITLE should be exactly right."""
        from kloudkompass.tui.screens import BRAND_TITLE
        assert BRAND_TITLE == "Kloud Kompass – Multicloud Analytix"
    
    def test_brand_short_exists(self):
        """BRAND_SHORT should be defined."""
        from kloudkompass.tui.screens import BRAND_SHORT
        assert BRAND_SHORT is not None
    
    def test_brand_short_exact_value(self):
        """BRAND_SHORT should be exactly right."""
        from kloudkompass.tui.screens import BRAND_SHORT
        assert BRAND_SHORT == "Kloud Kompass"
    
    def test_brand_title_contains_multicloud(self):
        """BRAND_TITLE should mention Multicloud."""
        from kloudkompass.tui.screens import BRAND_TITLE
        assert "Multicloud" in BRAND_TITLE
    
    def test_brand_title_contains_analytix(self):
        """BRAND_TITLE should mention Analytix."""
        from kloudkompass.tui.screens import BRAND_TITLE
        assert "Analytix" in BRAND_TITLE


class TestScreenBranding:
    """Tests that screens use centralized branding."""
    
    def test_main_menu_uses_brand_title(self):
        """MainMenuScreen should use BRAND_TITLE."""
        from kloudkompass.tui.main_menu import MainMenuScreen
        from kloudkompass.tui.screens import BRAND_TITLE
        
        screen = MainMenuScreen()
        assert screen.title == BRAND_TITLE
    
    def test_screen_default_title_is_brand(self):
        """Screen base class default title should be BRAND_TITLE."""
        from kloudkompass.tui.screens import Screen, BRAND_TITLE
        assert Screen.title == BRAND_TITLE
    
    def test_main_menu_imports_brand_title(self):
        """main_menu.py should import BRAND_TITLE."""
        from kloudkompass.tui import main_menu
        source = inspect.getsource(main_menu)
        assert 'BRAND_TITLE' in source
    
    def test_cost_menu_no_hardcoded_brand(self):
        """cost_menu.py should not hardcode 'Kloud Kompass – Multicloud'."""
        from kloudkompass.tui import cost_menu
        source = inspect.getsource(cost_menu)
        # Should not contain hardcoded brand string
        assert 'Kloud Kompass – Multicloud' not in source


class TestDoctorBranding:
    """Tests that doctor uses centralized branding."""
    
    def test_doctor_imports_brand_title(self):
        """doctor.py should import BRAND_TITLE."""
        from kloudkompass.tui import doctor
        source = inspect.getsource(doctor)
        assert 'BRAND_TITLE' in source
    
    def test_doctor_uses_brand_in_header(self):
        """print_doctor_report should use BRAND_TITLE."""
        from kloudkompass.tui import doctor
        source = inspect.getsource(doctor.print_doctor_report)
        assert 'BRAND_TITLE' in source


class TestNoBrandingLiterals:
    """Tests that branding is not hardcoded elsewhere."""
    
    def test_inventory_menu_no_hardcoded_brand(self):
        """inventory_menu.py should not hardcode full brand."""
        from kloudkompass.tui import inventory_menu
        source = inspect.getsource(inventory_menu)
        assert 'Kloud Kompass – Multicloud Analytix' not in source
    
    def test_security_menu_no_hardcoded_brand(self):
        """security_menu.py should not hardcode full brand."""
        from kloudkompass.tui import security_menu
        source = inspect.getsource(security_menu)
        assert 'Kloud Kompass – Multicloud Analytix' not in source


class TestNavHintConsistency:
    """Tests for navigation hint consistency."""
    
    def test_nav_hint_exists(self):
        """NAV_HINT should be defined."""
        from kloudkompass.tui.screens import NAV_HINT
        assert NAV_HINT is not None
    
    def test_nav_hint_contains_b_for_back(self):
        """NAV_HINT should show B for back."""
        from kloudkompass.tui.screens import NAV_HINT
        assert "[B]" in NAV_HINT
        assert "Back" in NAV_HINT
    
    def test_nav_hint_contains_q_for_quit(self):
        """NAV_HINT should show Q for quit."""
        from kloudkompass.tui.screens import NAV_HINT
        assert "[Q]" in NAV_HINT
        assert "Quit" in NAV_HINT
