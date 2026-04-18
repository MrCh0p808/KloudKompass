# tests/test_compute_menu.py
# --------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Compute TUI menu tests — menu structure, region gate, routing.

import pytest
import inspect


class TestComputeMenuStructure:
    """Tests for ComputeMenuScreen class structure."""

    def test_import_compute_menu(self):
        from kloudkompass.tui.compute_menu import ComputeMenuScreen
        assert ComputeMenuScreen is not None

    def test_menu_has_render_method(self):
        from kloudkompass.tui.compute_menu import ComputeMenuScreen
        assert hasattr(ComputeMenuScreen, "render")

    def test_menu_has_list_instances(self):
        from kloudkompass.tui.compute_menu import ComputeMenuScreen
        assert hasattr(ComputeMenuScreen, "_list_instances")

    def test_menu_has_filter_by_tag(self):
        from kloudkompass.tui.compute_menu import ComputeMenuScreen
        assert hasattr(ComputeMenuScreen, "_filter_by_tag")


class TestComputeMenuImports:
    """Verify the compute menu imports the region gate."""

    def test_imports_ensure_region_configured(self):
        from kloudkompass.tui import compute_menu
        source = inspect.getsource(compute_menu)
        assert "ensure_region_configured" in source

    def test_imports_get_session(self):
        from kloudkompass.tui import compute_menu
        source = inspect.getsource(compute_menu)
        assert "get_session" in source

    def test_imports_ensure_provider_configured(self):
        from kloudkompass.tui import compute_menu
        source = inspect.getsource(compute_menu)
        assert "ensure_provider_configured" in source
