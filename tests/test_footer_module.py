# tests/test_footer_module.py
# -----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 footer module tests (20 tests).

import pytest
from unittest.mock import patch, MagicMock


class TestAttributionConstants:
    """Tests for attribution constants."""
    
    def test_line1_exists(self):
        from kloudkompass.tui.footer import ATTRIBUTION_LINE1
        assert ATTRIBUTION_LINE1 is not None
    
    def test_line2_exists(self):
        from kloudkompass.tui.footer import ATTRIBUTION_LINE2
        assert ATTRIBUTION_LINE2 is not None
    
    def test_line1_has_year(self):
        from kloudkompass.tui.footer import ATTRIBUTION_LINE1
        assert "2026" in ATTRIBUTION_LINE1
    
    def test_line1_has_company(self):
        from kloudkompass.tui.footer import ATTRIBUTION_LINE1
        assert "TTox.Tech" in ATTRIBUTION_LINE1
    
    def test_line2_is_empty(self):
        from kloudkompass.tui.footer import ATTRIBUTION_LINE2
        assert ATTRIBUTION_LINE2 == ""
    
    def test_full_combines_lines(self):
        from kloudkompass.tui.footer import ATTRIBUTION_FULL, ATTRIBUTION_LINE1, ATTRIBUTION_LINE2
        assert ATTRIBUTION_LINE1 in ATTRIBUTION_FULL
        assert ATTRIBUTION_LINE2 in ATTRIBUTION_FULL
    
    def test_short_exists(self):
        from kloudkompass.tui.footer import ATTRIBUTION_SHORT
        assert "TTox.Tech" in ATTRIBUTION_SHORT
    
    def test_legacy_footer_text(self):
        from kloudkompass.tui.footer import FOOTER_TEXT, ATTRIBUTION_LINE1
        assert FOOTER_TEXT == ATTRIBUTION_LINE1
    
    def test_legacy_footer_legal(self):
        from kloudkompass.tui.footer import FOOTER_LEGAL, ATTRIBUTION_LINE2
        assert FOOTER_LEGAL == ATTRIBUTION_LINE2


class TestGetFooterText:
    """Tests for get_footer_text()."""
    
    def test_returns_string(self):
        from kloudkompass.tui.footer import get_footer_text
        assert isinstance(get_footer_text(), str)
    
    def test_contains_attribution(self):
        from kloudkompass.tui.footer import get_footer_text
        result = get_footer_text()
        assert "TTox.Tech" in result
    
    def test_contains_both_lines(self):
        from kloudkompass.tui.footer import get_footer_text, ATTRIBUTION_LINE1, ATTRIBUTION_LINE2
        result = get_footer_text()
        assert ATTRIBUTION_LINE1 in result
        assert ATTRIBUTION_LINE2 in result


class TestGetAttributionLines:
    """Tests for get_attribution_lines()."""
    
    def test_returns_tuple(self):
        from kloudkompass.tui.footer import get_attribution_lines
        result = get_attribution_lines()
        assert isinstance(result, tuple)
    
    def test_tuple_length_two(self):
        from kloudkompass.tui.footer import get_attribution_lines
        result = get_attribution_lines()
        assert len(result) == 2
    
    def test_first_matches_line1(self):
        from kloudkompass.tui.footer import get_attribution_lines, ATTRIBUTION_LINE1
        line1, _ = get_attribution_lines()
        assert line1 == ATTRIBUTION_LINE1
    
    def test_second_matches_line2(self):
        from kloudkompass.tui.footer import get_attribution_lines, ATTRIBUTION_LINE2
        _, line2 = get_attribution_lines()
        assert line2 == ATTRIBUTION_LINE2


class TestRenderFooter:
    """Tests for render_footer()."""
    
    def test_plain_print(self):
        from kloudkompass.tui.footer import render_footer
        output = []
        with patch('builtins.print', side_effect=lambda *a, **kw: output.append(str(a))):
            render_footer()
        full = "\n".join(output)
        assert "TTox.Tech" in full
    
    def test_plain_print_no_exception(self):
        from kloudkompass.tui.footer import render_footer
        with patch('builtins.print'):
            render_footer()  # Should not raise
