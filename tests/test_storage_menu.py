# tests/test_storage_menu.py
# --------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Storage TUI menu tests — structure, imports, region gate.

import pytest
import inspect


class TestStorageMenuStructure:
    def test_import_storage_menu(self):
        from kloudkompass.tui.storage_menu import StorageMenuScreen
        assert StorageMenuScreen is not None

    def test_has_list_buckets(self):
        from kloudkompass.tui.storage_menu import StorageMenuScreen
        assert hasattr(StorageMenuScreen, "_list_buckets")

    def test_has_list_volumes(self):
        from kloudkompass.tui.storage_menu import StorageMenuScreen
        assert hasattr(StorageMenuScreen, "_list_volumes")

    def test_has_find_unattached(self):
        from kloudkompass.tui.storage_menu import StorageMenuScreen
        assert hasattr(StorageMenuScreen, "_find_unattached")


class TestStorageMenuImports:
    def test_has_region_gate(self):
        from kloudkompass.tui import storage_menu
        source = inspect.getsource(storage_menu)
        assert "ensure_region_configured" in source

    def test_has_get_session(self):
        from kloudkompass.tui import storage_menu
        source = inspect.getsource(storage_menu)
        assert "get_session" in source
