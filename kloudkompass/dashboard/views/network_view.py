# kloudkompass/dashboard/views/network_view.py
# --------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Network (VPC/Subnet/SG) dashboard view with tabbed interface.

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, DataTable, TabbedContent, TabPane, Input
from textual.binding import Binding
import re


class NetworkView(Container):
    """
    Network resources dashboard view.

    Tabbed interface: VPCs / Subnets / Security Groups.
    Each tab has its own DataTable loaded on selection.
    """

    DEFAULT_CSS = """
    NetworkView {
        height: 100%;
        width: 100%;
    }

    NetworkView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }

    NetworkView .search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }

    NetworkView .status-line {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear Filters"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_vpcs = []
        self.all_subnets = []
        self.all_sgs = []
        self.current_search = ""

    def compose(self) -> ComposeResult:
        yield Static("🌐 Network Resources (VPC)", classes="view-title")
        with Container(classes="search-bar"):
            yield Input(placeholder="Search... ( / to focus, Esc to clear )", id="network_search_input")
        with TabbedContent():
            with TabPane("VPCs", id="tab_vpcs"):
                yield DataTable(id="vpc_table")
            with TabPane("Subnets", id="tab_subnets"):
                yield DataTable(id="subnet_table")
            with TabPane("Security Groups", id="tab_sgs"):
                yield DataTable(id="sg_table")
        yield Static("Select a tab to load data.", classes="status-line", id="network_status")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "network_search_input":
            self.current_search = event.value.strip().lower()
            self._render_vpcs()
            self._render_subnets()
            self._render_sgs()

    def action_focus_search(self) -> None:
        self.query_one("#network_search_input").focus()

    def action_clear_search(self) -> None:
        self.query_one("#network_search_input", Input).value = ""
        self.current_search = ""
        self._render_vpcs()
        self._render_subnets()
        self._render_sgs()

    def on_tabbed_content_tab_activated(self, event) -> None:
        tab_id = event.tab.id if hasattr(event, "tab") else None
        
        # Load saved search
        if not self.current_search:
            from kloudkompass.config_manager import get_config_value
            saved = get_config_value("network_saved_search", "")
            if saved:
                self.current_search = saved
                self.query_one("#network_search_input", Input).value = saved

        if tab_id and "vpcs" in str(tab_id):
            self._load_vpcs()
        elif tab_id and "subnets" in str(tab_id):
            self._load_subnets()
        elif tab_id and "sgs" in str(tab_id):
            self._load_sgs()

    def _load_vpcs(self) -> None:
        table = self.query_one("#vpc_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_vpcs(), name="fetch_vpcs", exclusive=True)

    def _load_subnets(self) -> None:
        table = self.query_one("#subnet_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_subnets(), name="fetch_subnets", exclusive=True)

    def _load_sgs(self) -> None:
        table = self.query_one("#sg_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_sgs(), name="fetch_sgs", exclusive=True)

    async def _fetch_vpcs(self) -> None:
        status = self.query_one("#network_status", Static)
        table = self.query_one("#vpc_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_network_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_network_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread to prevent blocking the UI
            self.all_vpcs = await asyncio.to_thread(
                provider.list_vpcs,
                region=config.get("default_region", "us-east-1"),
                profile=config.get("default_profile"),
            )
            self.call_from_thread(self._render_vpcs)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_vpcs(self) -> None:
        table = self.query_one("#vpc_table", DataTable)
        status = self.query_one("#network_status", Static)
        
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("network_saved_search", self.current_search)
        except Exception: pass

        table.clear()
        count = 0
        tag_key, tag_val = None, None
        is_tag_search = self.current_search.startswith("tag:")
        if is_tag_search:
            parts = self.current_search[4:].split("=", 1)
            if len(parts) == 2:
                tag_key, tag_val = parts[0].strip(), parts[1].strip()

        for vpc in self.all_vpcs:
            search_str = f"{vpc.vpc_id} {vpc.name} {vpc.cidr_block}".lower()
            if self.current_search:
                if is_tag_search and tag_key and tag_val:
                    match = False
                    for tk, tv in vpc.tags.items():
                        if tk.lower() == tag_key and tag_val in tv.lower():
                            match = True; break
                    if not match: continue
                else:
                    try:
                        if not re.search(self.current_search, search_str): continue
                    except re.error:
                        if self.current_search not in search_str: continue

            table.add_row(vpc.vpc_id, vpc.name[:25], vpc.cidr_block, vpc.state, "✓" if vpc.is_default else "")
            count += 1
        status.update(f"Found {count}/{len(self.all_vpcs)} VPC(s)")

    async def _fetch_subnets(self) -> None:
        status = self.query_one("#network_status", Static)
        table = self.query_one("#subnet_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_network_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_network_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread to prevent blocking the UI
            self.all_subnets = await asyncio.to_thread(
                provider.list_subnets,
                region=config.get("default_region", "us-east-1"),
                profile=config.get("default_profile"),
            )
            self.call_from_thread(self._render_subnets)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_subnets(self) -> None:
        table = self.query_one("#subnet_table", DataTable)
        status = self.query_one("#network_status", Static)
        table.clear()
        count = 0
        
        tag_key, tag_val = None, None
        is_tag_search = self.current_search.startswith("tag:")
        if is_tag_search:
            parts = self.current_search[4:].split("=", 1)
            if len(parts) == 2:
                tag_key, tag_val = parts[0].strip(), parts[1].strip()

        for s in self.all_subnets:
            search_str = f"{s.subnet_id} {s.name} {s.cidr_block} {s.availability_zone}".lower()
            if self.current_search:
                if is_tag_search and tag_key and tag_val:
                    match = False
                    for tk, tv in s.tags.items():
                        if tk.lower() == tag_key and tag_val in tv.lower():
                            match = True; break
                    if not match: continue
                else:
                    try:
                        if not re.search(self.current_search, search_str): continue
                    except re.error:
                        if self.current_search not in search_str: continue

            table.add_row(s.subnet_id, s.name[:20], s.cidr_block, s.availability_zone, str(s.available_ips), "✓" if s.is_public else "")
            count += 1
        status.update(f"Found {count}/{len(self.all_subnets)} subnet(s)")

    async def _fetch_sgs(self) -> None:
        status = self.query_one("#network_status", Static)
        try:
            from kloudkompass.core.provider_factory import get_network_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_network_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread to prevent blocking the UI
            self.all_sgs = await asyncio.to_thread(
                provider.list_security_groups,
                region=config.get("default_region", "us-east-1"),
                profile=config.get("default_profile"),
            )
            self.call_from_thread(self._render_sgs)
        except Exception as e:
            status.update(f"Error: {e}")
            table = self.query_one("#sg_table", DataTable)
            table.loading = False

    def _render_sgs(self) -> None:
        table = self.query_one("#sg_table", DataTable)
        status = self.query_one("#network_status", Static)
        table.clear()
        count = 0
        
        tag_key, tag_val = None, None
        is_tag_search = self.current_search.startswith("tag:")
        if is_tag_search:
            parts = self.current_search[4:].split("=", 1)
            if len(parts) == 2:
                tag_key, tag_val = parts[0].strip(), parts[1].strip()

        for sg in self.all_sgs:
            search_str = f"{sg.group_id} {sg.name} {sg.vpc_id}".lower()
            if self.current_search:
                if is_tag_search and tag_key and tag_val:
                    match = False
                    for tk, tv in sg.tags.items():
                        if tk.lower() == tag_key and tag_val in tv.lower():
                            match = True; break
                    if not match: continue
                else:
                    try:
                        if not re.search(self.current_search, search_str): continue
                    except re.error:
                        if self.current_search not in search_str: continue

            table.add_row(sg.group_id, sg.name[:25], sg.vpc_id, str(len(sg.inbound_rules)), str(len(sg.outbound_rules)))
            count += 1
        status.update(f"Found {count}/{len(self.all_sgs)} security group(s)")
