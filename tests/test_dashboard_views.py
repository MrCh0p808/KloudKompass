# tests/test_dashboard_views.py
# -----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Smoke tests for dashboard views, sidebar, settings modal, and app registry.

import pytest
from unittest.mock import patch


# ────────────────────────────────────────────────────
#  Import smoke tests — every view must import cleanly.
# ────────────────────────────────────────────────────

class TestViewImports:
    """Verify all dashboard views import without errors."""

    def test_import_cost_view(self):
        from kloudkompass.dashboard.views.cost_view import CostView
        assert CostView is not None

    def test_import_compute_view(self):
        from kloudkompass.dashboard.views.compute_view import ComputeView
        assert ComputeView is not None

    def test_import_network_view(self):
        from kloudkompass.dashboard.views.network_view import NetworkView
        assert NetworkView is not None

    def test_import_storage_view(self):
        from kloudkompass.dashboard.views.storage_view import StorageView
        assert StorageView is not None

    def test_import_iam_view(self):
        from kloudkompass.dashboard.views.iam_view import IAMView
        assert IAMView is not None

    def test_import_database_view(self):
        from kloudkompass.dashboard.views.database_view import DatabaseView
        assert DatabaseView is not None

    def test_import_security_view(self):
        from kloudkompass.dashboard.views.security_view import SecurityView
        assert SecurityView is not None

    def test_import_doctor_view(self):
        from kloudkompass.dashboard.views.doctor_view import DoctorView
        assert DoctorView is not None


# ────────────────────────────────────────────────────
#  Settings Modal import + structure
# ────────────────────────────────────────────────────

class TestSettingsModalImport:
    """Verify Settings Modal imports and has required constants."""

    def test_import_settings_modal(self):
        from kloudkompass.dashboard.widgets.settings_modal import SettingsModal
        assert SettingsModal is not None

    def test_region_options_defined(self):
        from kloudkompass.dashboard.widgets.settings_modal import REGION_OPTIONS
        assert isinstance(REGION_OPTIONS, list)
        assert len(REGION_OPTIONS) >= 4

    def test_provider_options_defined(self):
        from kloudkompass.dashboard.widgets.settings_modal import PROVIDER_OPTIONS
        assert isinstance(PROVIDER_OPTIONS, list)
        assert len(PROVIDER_OPTIONS) >= 3

    def test_provider_options_include_aws(self):
        from kloudkompass.dashboard.widgets.settings_modal import PROVIDER_OPTIONS
        providers = [p[1] for p in PROVIDER_OPTIONS]
        assert "aws" in providers

    def test_region_options_include_us_east_1(self):
        from kloudkompass.dashboard.widgets.settings_modal import REGION_OPTIONS
        regions = [r[1] for r in REGION_OPTIONS]
        assert "us-east-1" in regions


# ────────────────────────────────────────────────────
#  App: VIEW_REGISTRY structure
# ────────────────────────────────────────────────────

class TestViewRegistry:
    """Verify the VIEW_REGISTRY maps all 8 views correctly."""

    def test_registry_has_8_views(self):
        from kloudkompass.dashboard.widgets.workspace_shell import VIEW_REGISTRY
        assert len(VIEW_REGISTRY) == 8

    def test_registry_contains_all_view_names(self):
        from kloudkompass.dashboard.widgets.workspace_shell import VIEW_REGISTRY
        expected = {"cost", "compute", "network", "storage", "iam", "database", "security", "doctor"}
        assert set(VIEW_REGISTRY.keys()) == expected

    def test_registry_values_are_classes(self):
        from kloudkompass.dashboard.widgets.workspace_shell import VIEW_REGISTRY
        for name, cls in VIEW_REGISTRY.items():
            assert isinstance(cls, type), f"{name} → {cls} is not a class"

    def test_registry_cost_maps_to_cost_view(self):
        from kloudkompass.dashboard.widgets.workspace_shell import VIEW_REGISTRY
        from kloudkompass.dashboard.views.cost_view import CostView
        assert VIEW_REGISTRY["cost"] is CostView

    def test_registry_compute_maps_to_compute_view(self):
        from kloudkompass.dashboard.widgets.workspace_shell import VIEW_REGISTRY
        from kloudkompass.dashboard.views.compute_view import ComputeView
        assert VIEW_REGISTRY["compute"] is ComputeView


# ────────────────────────────────────────────────────
#  App: KloudKompassApp class structure
# ────────────────────────────────────────────────────

class TestKloudKompassAppStructure:
    """Verify the app class has the expected attributes and bindings."""

    def test_app_has_title(self):
        from kloudkompass.dashboard.app import KloudKompassApp
        assert "Kloud Kompass" in KloudKompassApp.TITLE

    def test_app_has_sub_title(self):
        from kloudkompass.dashboard.app import KloudKompassApp
        assert KloudKompassApp.SUB_TITLE == "Management OS"

    def test_app_has_bindings(self):
        from kloudkompass.dashboard.app import KloudKompassApp
        assert len(KloudKompassApp.BINDINGS) >= 8

    def test_workspace_init_sets_current_view(self):
        from kloudkompass.dashboard.widgets.workspace_shell import Workspace
        from kloudkompass.core.workspace_registry import WorkspaceContext
        context = WorkspaceContext(id="test", provider="aws", last_view="cost")
        workspace = Workspace(context)
        assert workspace.current_view == "cost"


# ────────────────────────────────────────────────────
#  Sidebar structure
# ────────────────────────────────────────────────────

class TestSidebarStructure:
    """Verify the sidebar has the correct buttons."""

    def test_sidebar_is_vertical(self):
        from kloudkompass.dashboard.widgets.workspace_shell import DynamicSidebar
        from textual.containers import Vertical
        assert issubclass(DynamicSidebar, Vertical)

    def test_sidebar_has_compose_method(self):
        from kloudkompass.dashboard.widgets.workspace_shell import DynamicSidebar
        assert hasattr(DynamicSidebar, "compose")
