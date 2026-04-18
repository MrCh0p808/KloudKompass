# kloudkompass/dashboard/views/iam_view.py
# ----------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# IAM (Users/Roles/Policies) dashboard view with tabbed interface.

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, DataTable, TabbedContent, TabPane, Input
from textual.binding import Binding
import re


class IAMView(Container):
    """
    IAM resources dashboard view.

    Tabbed interface: Users / Roles / Policies.
    """

    DEFAULT_CSS = """
    IAMView {
        height: 100%;
        width: 100%;
    }

    IAMView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }

    IAMView .search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }

    IAMView .status-line {
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
        self.all_users = []
        self.all_roles = []
        self.all_policies = []
        self.current_search = ""

    def compose(self) -> ComposeResult:
        yield Static("🔐 IAM Resources", classes="view-title")
        with Container(classes="search-bar"):
            yield Input(placeholder="Search... ( / to focus, Esc to clear )", id="iam_search_input")
        with TabbedContent():
            with TabPane("Users", id="tab_users"):
                yield DataTable(id="user_table")
            with TabPane("Roles", id="tab_roles"):
                yield DataTable(id="role_table")
            with TabPane("Policies", id="tab_policies"):
                yield DataTable(id="policy_table")
        yield Static("Select a tab to load IAM data.", classes="status-line", id="iam_status")

    def on_mount(self) -> None:
        ut = self.query_one("#user_table", DataTable)
        ut.add_columns("User Name", "User ID", "Created", "MFA", "Access Keys")

        rt = self.query_one("#role_table", DataTable)
        rt.add_columns("Role Name", "Role ID", "Created", "Path")

        pt = self.query_one("#policy_table", DataTable)
        pt.add_columns("Policy Name", "ARN", "Attached", "Type")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "iam_search_input":
            self.current_search = event.value.strip().lower()
            self._render_users()
            self._render_roles()
            self._render_policies()

    def action_focus_search(self) -> None:
        self.query_one("#iam_search_input").focus()

    def action_clear_search(self) -> None:
        self.query_one("#iam_search_input", Input).value = ""
        self.current_search = ""
        self._render_users()
        self._render_roles()
        self._render_policies()

    def on_tabbed_content_tab_activated(self, event) -> None:
        tab_id = str(getattr(event, "tab", ""))
        # Load saved search on mount
        if not self.current_search:
            from kloudkompass.config_manager import get_config_value
            saved = get_config_value("iam_saved_search", "")
            if saved:
                self.current_search = saved
                self.query_one("#iam_search_input", Input).value = saved

        if "users" in tab_id:
            self._load_users()
        elif "roles" in tab_id:
            self._load_roles()
        elif "policies" in tab_id:
            self._load_policies()

    def _load_users(self) -> None:
        table = self.query_one("#user_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_users(), name="fetch_users", exclusive=True)

    def _load_roles(self) -> None:
        table = self.query_one("#role_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_roles(), name="fetch_roles", exclusive=True)

    def _load_policies(self) -> None:
        table = self.query_one("#policy_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_policies(), name="fetch_policies", exclusive=True)

    async def _fetch_users(self) -> None:
        status = self.query_one("#iam_status", Static)
        table = self.query_one("#user_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_iam_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_iam_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread
            self.all_users = await asyncio.to_thread(
                provider.list_users,
                profile=config.get("default_profile")
            )
            self.call_from_thread(self._render_users)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_users(self) -> None:
        table = self.query_one("#user_table", DataTable)
        status = self.query_one("#iam_status", Static)
        
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("iam_saved_search", self.current_search)
        except Exception: pass

        table.clear()
        count = 0
        for u in self.all_users:
            search_str = f"{u.user_name} {u.user_id} {u.arn}".lower()
            if self.current_search:
                try:
                    if not re.search(self.current_search, search_str): continue
                except re.error:
                    if self.current_search not in search_str: continue

            mfa = "[green]✓[/]" if u.mfa_enabled else "[red]✗[/]"
            keys = str(u.access_keys) if hasattr(u, "access_keys") else "—"
            table.add_row(u.user_name, u.user_id, u.create_date[:10] if u.create_date else "—", mfa, keys)
            count += 1
        status.update(f"Found {count}/{len(self.all_users)} user(s)")

    async def _fetch_roles(self) -> None:
        status = self.query_one("#iam_status", Static)
        table = self.query_one("#role_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_iam_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_iam_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread
            self.all_roles = await asyncio.to_thread(
                provider.list_roles,
                profile=config.get("default_profile")
            )
            self.call_from_thread(self._render_roles)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_roles(self) -> None:
        table = self.query_one("#role_table", DataTable)
        status = self.query_one("#iam_status", Static)
        table.clear()
        count = 0
        for r in self.all_roles:
            search_str = f"{r.role_name} {r.role_id} {r.arn}".lower()
            if self.current_search:
                if self.current_search not in search_str: continue
            table.add_row(r.role_name, r.role_id, r.create_date[:10] if r.create_date else "—", r.path)
            count += 1
        status.update(f"Found {count}/{len(self.all_roles)} role(s)")

    async def _fetch_policies(self) -> None:
        status = self.query_one("#iam_status", Static)
        table = self.query_one("#policy_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_iam_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_iam_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread
            self.all_policies = await asyncio.to_thread(
                provider.list_policies,
                profile=config.get("default_profile")
            )
            self.call_from_thread(self._render_policies)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table = self.query_one("#policy_table", DataTable)
            table.loading = False

    def _render_policies(self) -> None:
        table = self.query_one("#policy_table", DataTable)
        status = self.query_one("#iam_status", Static)
        table.clear()
        count = 0
        for p in self.all_policies:
            search_str = f"{p.policy_name} {p.arn}".lower()
            if self.current_search:
                if self.current_search not in search_str: continue
            policy_type = "AWS" if "aws-policy" in (p.arn or "") else "Custom"
            table.add_row(p.policy_name, p.arn or "—", str(p.attachment_count), policy_type)
            count += 1
        status.update(f"Found {count}/{len(self.all_policies)} policy(ies)")
