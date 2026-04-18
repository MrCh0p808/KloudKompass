# tests/test_network_menu.py
# --------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Network TUI menu tests — structure, imports, region gate.

import pytest
import inspect


class TestNetworkMenuStructure:
    def test_import_network_menu(self):
        from kloudkompass.tui.network_menu import NetworkMenuScreen
        assert NetworkMenuScreen is not None

    def test_has_list_vpcs(self):
        from kloudkompass.tui.network_menu import NetworkMenuScreen
        assert hasattr(NetworkMenuScreen, "_list_vpcs")

    def test_has_list_subnets(self):
        from kloudkompass.tui.network_menu import NetworkMenuScreen
        assert hasattr(NetworkMenuScreen, "_list_subnets")

    def test_has_list_security_groups(self):
        from kloudkompass.tui.network_menu import NetworkMenuScreen
        assert hasattr(NetworkMenuScreen, "_list_security_groups")

    def test_has_view_sg_rules(self):
        from kloudkompass.tui.network_menu import NetworkMenuScreen
        assert hasattr(NetworkMenuScreen, "_view_sg_rules")


class TestNetworkMenuImports:
    def test_has_region_gate(self):
        from kloudkompass.tui import network_menu
        source = inspect.getsource(network_menu)
        assert "ensure_region_configured" in source

    def test_has_get_session(self):
        from kloudkompass.tui import network_menu
        source = inspect.getsource(network_menu)
        assert "get_session" in source

    def test_has_provider_gate(self):
        from kloudkompass.tui import network_menu
        source = inspect.getsource(network_menu)
        assert "ensure_provider_configured" in source
