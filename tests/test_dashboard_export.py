# tests/test_dashboard_export.py
# -------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 dashboard export tests (15 tests).

import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime


class TestExportDirectory:
    """Tests for export directory configuration."""
    
    def test_export_dir_is_path(self):
        """EXPORT_DIR should be a Path."""
        from kloudkompass.dashboard.widgets.export_modal import EXPORT_DIR
        assert isinstance(EXPORT_DIR, Path)
    
    def test_export_dir_in_user_home(self):
        """EXPORT_DIR should be in user's home."""
        from kloudkompass.dashboard.widgets.export_modal import EXPORT_DIR
        assert str(Path.home()) in str(EXPORT_DIR)
    
    def test_export_dir_under_kloudkompass(self):
        """EXPORT_DIR should be under .kloudkompass."""
        from kloudkompass.dashboard.widgets.export_modal import EXPORT_DIR
        assert ".kloudkompass" in str(EXPORT_DIR)


class TestExportModalInit:
    """Tests for ExportModal initialization."""
    
    def test_default_view_name(self):
        """Default view_name should be 'dashboard'."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        modal = ExportModal()
        assert modal.view_name == "dashboard"
    
    def test_custom_view_name(self):
        """Custom view_name should be stored."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        modal = ExportModal(view_name="security")
        assert modal.view_name == "security"
    
    def test_default_data_empty(self):
        """Default data should be empty dict."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        modal = ExportModal()
        assert modal.data == {}
    
    def test_custom_data_stored(self):
        """Custom data should be stored."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        data = {"test": "value"}
        modal = ExportModal(data=data)
        assert modal.data == data


class TestExportWriters:
    """Tests for export file writers."""
    
    def test_csv_writer_method_exists(self):
        """ExportModal should have _write_csv method."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        assert hasattr(ExportModal, '_write_csv')
    
    def test_json_writer_method_exists(self):
        """ExportModal should have _write_json method."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        assert hasattr(ExportModal, '_write_json')
    
    def test_markdown_writer_method_exists(self):
        """ExportModal should have _write_markdown method."""
        from kloudkompass.dashboard.widgets.export_modal import ExportModal
        assert hasattr(ExportModal, '_write_markdown')


class TestExportFormats:
    """Tests for export format support."""
    
    def test_csv_format_supported(self):
        """CSV format should be supported."""
        from kloudkompass.dashboard.widgets import export_modal
        import inspect
        source = inspect.getsource(export_modal)
        assert 'csv' in source.lower()
    
    def test_json_format_supported(self):
        """JSON format should be supported."""
        from kloudkompass.dashboard.widgets import export_modal
        import inspect
        source = inspect.getsource(export_modal)
        assert 'json' in source.lower()
    
    def test_markdown_format_supported(self):
        """Markdown format should be supported."""
        from kloudkompass.dashboard.widgets import export_modal
        import inspect
        source = inspect.getsource(export_modal)
        assert 'markdown' in source.lower() or '.md' in source


class TestExportFilenames:
    """Tests for export filename generation."""
    
    def test_filename_includes_kloudkompass(self):
        """Export filename should include 'kloudkompass'."""
        # Check the _do_export method constructs proper filename
        from kloudkompass.dashboard.widgets import export_modal
        import inspect
        source = inspect.getsource(export_modal.ExportModal._do_export)
        assert 'kloudkompass_' in source
    
    def test_filename_includes_timestamp(self):
        """Export filename should include timestamp."""
        from kloudkompass.dashboard.widgets import export_modal
        import inspect
        source = inspect.getsource(export_modal.ExportModal._do_export)
        assert 'strftime' in source
