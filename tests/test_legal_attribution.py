# tests/test_legal_attribution.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Tests for legal attribution per Master Brief.

import pytest

from kloudkompass import __version__, __copyright__
from kloudkompass.tui.footer import FOOTER_TEXT, FOOTER_LEGAL, get_footer_text


class TestPackageAttribution:
    """Tests for package-level attribution."""
    
    def test_copyright_constant_exists(self):
        """__copyright__ should be defined."""
        assert __copyright__ is not None
    
    def test_copyright_contains_year(self):
        """Copyright should contain year."""
        assert "2026" in __copyright__
    
    def test_copyright_contains_company(self):
        """Copyright should contain company name."""
        assert "TTox.Tech" in __copyright__
    
    def test_copyright_contains_all_rights(self):
        """Copyright should contain full notice."""
        assert "Licensed under MIT" in __copyright__


class TestFooterAttribution:
    """Tests for TUI footer attribution."""
    
    def test_footer_text_contains_copyright(self):
        """Footer text should contain copyright symbol."""
        assert "©" in FOOTER_TEXT
    
    def test_footer_text_contains_year(self):
        """Footer text should contain year."""
        assert "2026" in FOOTER_TEXT
    
    def test_footer_text_contains_company(self):
        """Footer text should contain company name."""
        assert "TTox.Tech" in FOOTER_TEXT
    
    def test_footer_legal_is_open_source(self):
        """Footer legal text."""
        assert FOOTER_LEGAL == ""
    
    def test_get_footer_text_returns_full_attribution(self):
        """get_footer_text should return full attribution (Phase 2.5)."""
        from kloudkompass.tui.footer import ATTRIBUTION_FULL
        assert get_footer_text() == ATTRIBUTION_FULL


class TestVersionAttribution:
    """Tests for CLI version output."""
    
    def test_version_is_defined(self):
        """Version should be defined."""
        assert __version__ is not None
    
    def test_version_format(self):
        """Version should be semantic version format."""
        parts = __version__.split(".")
        assert len(parts) >= 2  # At least major.minor
