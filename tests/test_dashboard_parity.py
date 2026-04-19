# tests/test_dashboard_parity.py
# -------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 dashboard parity tests (15 tests).

import pytest
import inspect


class TestQuitConfirmModal:
    """Tests for quit confirmation modal."""
    
    def test_quit_modal_exists(self):
        """QuitConfirmModal should be importable."""
        from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
        assert QuitConfirmModal is not None
    
    def test_quit_modal_is_modal_screen(self):
        """QuitConfirmModal should be a ModalScreen."""
        from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
        from textual.screen import ModalScreen
        assert issubclass(QuitConfirmModal, ModalScreen)
    
    def test_quit_modal_has_compose(self):
        """QuitConfirmModal should have compose method."""
        from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
        assert hasattr(QuitConfirmModal, 'compose')
    
    def test_quit_modal_has_bindings(self):
        """QuitConfirmModal should have y/n/escape bindings."""
        from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
        bindings = QuitConfirmModal.BINDINGS
        keys = [b[0] for b in bindings]
        assert 'y' in keys
        assert 'n' in keys
        assert 'escape' in keys
    
    def test_quit_modal_has_confirm_actions(self):
        """QuitConfirmModal should have confirm actions."""
        from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
        assert hasattr(QuitConfirmModal, 'action_confirm_yes')
        assert hasattr(QuitConfirmModal, 'action_confirm_no')


class TestExportModal:
    """Tests for export modal."""
    
    def test_export_modal_exists(self):
        """ExportModal should be importable."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        assert ExportModal is not None
    
    def test_export_modal_is_modal_screen(self):
        """ExportModal should be a ModalScreen."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        from textual.screen import ModalScreen
        assert issubclass(ExportModal, ModalScreen)
    
    def test_export_dir_defined(self):
        """Export directory should be defined."""
        from kloudkompass.dashboard.widgets.export_modal import EXPORT_DIR
        assert EXPORT_DIR is not None
        assert ".kloudkompass" in str(EXPORT_DIR)
        assert "exports" in str(EXPORT_DIR)
    
    def test_export_modal_accepts_view_name(self):
        """ExportModal should accept view_name parameter."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        modal = ExportModal(view_name="cost")
        assert modal.view_name == "cost"
    
    def test_export_modal_accepts_data(self):
        """ExportModal should accept data parameter."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        data = {"headers": ["A", "B"], "rows": [[1, 2]]}
        modal = ExportModal(data=data)
        assert modal.data == data


class TestDashboardAppParity:
    """Tests for dashboard app parity with TUI."""
    
    def test_app_uses_brand_title(self):
        """KloudKompassApp should use BRAND_TITLE."""
        from kloudkompass.dashboard.app import KloudKompassApp
        from kloudkompass.tui.screens import BRAND_TITLE
        assert KloudKompassApp.TITLE == BRAND_TITLE
    
    def test_app_has_quit_action(self):
        """KloudKompassApp should have request_quit action."""
        from kloudkompass.dashboard.app import KloudKompassApp
        assert hasattr(KloudKompassApp, 'action_request_quit')
    
    def test_app_has_export_action(self):
        """KloudKompassApp should have export action."""
        from kloudkompass.dashboard.app import KloudKompassApp
        assert hasattr(KloudKompassApp, 'action_export')
    
    def test_app_has_help_action(self):
        """KloudKompassApp should have help action."""
        from kloudkompass.dashboard.app import KloudKompassApp
        assert hasattr(KloudKompassApp, 'action_show_help')
    
    def test_sidebar_uses_brand_short(self):
        """Sidebar should use BRAND_SHORT."""
        from kloudkompass.dashboard.widgets import workspace_shell
        from kloudkompass.tui.screens import BRAND_SHORT
        source = inspect.getsource(workspace_shell.DynamicSidebar)
        # Should use the brand_short property which was seeded from BRAND_SHORT
        assert 'brand_short' in source.lower()
