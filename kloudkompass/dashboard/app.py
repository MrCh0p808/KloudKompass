# kloudkompass/dashboard/app.py
# ---------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Main Textual application for dashboard mode.
# Full sidebar with 8 nav views + Settings modal.

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Static, Button
from textual.binding import Binding
from textual.command import Provider, Hit

from kloudkompass.dashboard.views.cost_view import CostView
from kloudkompass.dashboard.views.compute_view import ComputeView
from kloudkompass.dashboard.views.network_view import NetworkView
from kloudkompass.dashboard.views.storage_view import StorageView
from kloudkompass.dashboard.views.iam_view import IAMView
from kloudkompass.dashboard.views.database_view import DatabaseView
from kloudkompass.dashboard.views.security_view import SecurityView
from kloudkompass.dashboard.views.doctor_view import DoctorView
from kloudkompass.dashboard.widgets.attribution_footer import AttributionFooter
from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
from kloudkompass.dashboard.widgets.export_modal import ExportModal
from kloudkompass.dashboard.widgets.help_modal import HelpModal
from kloudkompass.dashboard.widgets.settings_modal import SettingsModal
from kloudkompass.dashboard.widgets.resource_summary import ResourceSummary
from kloudkompass.dashboard.widgets.alerts import ActiveAlerts
from kloudkompass.tui.screens import BRAND_TITLE, BRAND_SHORT, BRAND_BANNER


# Registry: view_name → View class
VIEW_REGISTRY = {
    "cost": CostView,
    "compute": ComputeView,
    "network": NetworkView,
    "storage": StorageView,
    "iam": IAMView,
    "database": DatabaseView,
    "security": SecurityView,
    "doctor": DoctorView,
}


class ViewCommandProvider(Provider):
    """Provides dashboard view navigation to the Command Palette."""
    async def search(self, query: str) -> None:
        matcher = self.matcher(query)
        for view_name in VIEW_REGISTRY.keys():
            title = f"View: {view_name.title()}"
            score = matcher.match(title)
            if score > 0:
                action_name = f"action_show_{view_name}"
                if hasattr(self.app, action_name):
                    cmd = getattr(self.app, action_name)
                    yield Hit(
                        score,
                        matcher.highlight(title),
                        cmd,
                        text=title,
                        help=f"Navigate to the {view_name.title()} dashboard"
                    )


class RefreshTimer(Static):
    """Visual countdown timer for auto-refresh."""
    
    DEFAULT_CSS = """
    RefreshTimer {
        width: 100%;
        text-align: center;
        color: $text-muted;
        margin-top: 1;
        margin-bottom: 0;
    }
    """
    
    def on_mount(self) -> None:
        self.update("⏱  05:00")


class Sidebar(Vertical):
    """
    Navigation sidebar with all module buttons + Settings.
    """

    DEFAULT_CSS = """
    Sidebar {
        width: 15%;
        min-width: 18;
        max-width: 25;
        background: $surface;
        border-right: solid $primary;
        padding: 1;
    }

    Sidebar Button {
        width: 100%;
        margin-bottom: 1;
    }

    Sidebar .sidebar-title {
        text-align: center;
        text-style: bold;
        padding: 1;
        margin-bottom: 1;
    }

    Sidebar .sidebar-divider {
        height: 1;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(BRAND_SHORT, classes="sidebar-title")
        yield Button("💰 Cost", id="nav_cost", variant="primary", tooltip="View detailed AWS cost analysis")
        yield Button("🖥️  Compute", id="nav_compute", tooltip="Manage EC2 instances")
        yield Button("🌐 Network", id="nav_network", tooltip="Inspect VPCs and Security Groups")
        yield Button("📦 Storage", id="nav_storage", tooltip="Audit S3 buckets and EBS volumes")
        yield Button("🔐 IAM", id="nav_iam", tooltip="Identity & Access Management")
        yield Button("🗄️  Database", id="nav_database", tooltip="Monitor RDS and DynamoDB")
        yield Button("🛡️  Security", id="nav_security", tooltip="Run security audits and checks")
        yield Button("🩺 Doctor", id="nav_doctor", tooltip="System health check and diagnostic tool")
        yield Static("", classes="sidebar-divider")
        yield RefreshTimer(id="refresh_timer")
        yield Button("⚙️  Settings", id="nav_settings", tooltip="Configure profile and regions")


class ContentPanel(Container):
    """
    Main content panel — views are mounted/unmounted dynamically.
    """

    DEFAULT_CSS = """
    ContentPanel {
        width: 1fr;
        height: 100%;
        layout: vertical;
    }
    
    ContentPanel .breadcrumb-bar {
        dock: top;
        height: 1;
        background: $surface;
        color: $text-muted;
        padding-left: 2;
        border-bottom: solid $primary;
    }
    """

    def compose(self) -> ComposeResult:
        # Breadcrumbs bar
        yield Static("🏠 Dashboard > [b]Cost[/b]", id="breadcrumbs", classes="breadcrumb-bar")
        yield ResourceSummary(id="resource_summary")
        yield ActiveAlerts(id="active_alerts")
        # Start without a view, let on_mount attach the correct persisted view
        yield Container(id="view_placeholder", classes="placeholder-container")

class KloudKompassApp(App):
    """
    Main Kloud Kompass dashboard application.

    Full terminal dashboard with 8 module views, keyboard navigation,
    export, settings modal, and async operations.
    """

    TITLE = BRAND_TITLE
    SUB_TITLE = "Dashboard"
    
    ENABLE_COMMAND_PALETTE = True

    # Add custom command provider to the default App.COMMANDS
    COMMANDS = App.COMMANDS | {ViewCommandProvider}

    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #app_banner {
        dock: top;
        width: 100%;
        height: auto;
        content-align: center middle;
        color: $secondary;
        background: $surface-darken-1;
        border-bottom: solid $primary;
        padding: 0 2;
    }
    #resource_summary {
        dock: top;
        width: 100%;
        height: 1;
        content-align: center middle;
        background: $boost;
        color: $text;
        text-style: bold;
        border-bottom: solid $primary;
    }
    
    /* Global Neuromorphic Palette */
    Button:hover {
        background: $accent;
        color: $text-accent;
        text-style: reverse;
        transition: background 250ms;
    }
    
    DataTable {
        border: tall $primary-muted;
        background: $surface;
        zebra_stripes: True;
    }
    
    DataTable > .datatable--cursor {
        background: $secondary-muted;
        color: $text;
        text-style: bold;
    }

    .placeholder-container {
        align: center middle;
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "request_quit", "Quit", show=True),
        Binding("e", "export", "Export", show=True),
        Binding("1", "show_cost", "Cost"),
        Binding("2", "show_compute", "Compute"),
        Binding("3", "show_network", "Network"),
        Binding("4", "show_storage", "Storage"),
        Binding("5", "show_iam", "IAM"),
        Binding("6", "show_database", "Database"),
        Binding("7", "show_security", "Security"),
        Binding("8", "show_doctor", "Doctor"),
        Binding("r", "refresh", "Refresh"),
        Binding("f5", "force_refresh", "Force Refresh"),
        Binding("d", "toggle_dark", "Toggle Dark/Light Mode"),
        Binding("[", "toggle_sidebar", "Toggle Sidebar"),
        Binding("ctrl+k", "command_palette", "Command Palette"),
        Binding("?", "show_help", "Help"),
        Binding("u", "undo", "Undo Action", show=True),
        Binding("tab", "cycle_focus", "Cycle Focus", show=False),
        Binding("shift+tab", "cycle_focus_reverse", "Reverse Focus", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from kloudkompass.config_manager import get_config_value
        last_view = get_config_value("last_dashboard_view", "cost")
        
        # Validate saved view exists to prevent crashes
        if last_view not in VIEW_REGISTRY:
            last_view = "cost"
            
        self.current_view = last_view
        self._current_data = {}
        self.refresh_timer_seconds = 300

    def compose(self) -> ComposeResult:
        """Build the main application layout."""
        yield Header()
        banner = Static(BRAND_BANNER, id="app_banner")
        banner.markup = False
        yield banner
        
        # Mount the Sidebar but initialize proper component focus
        sidebar = Sidebar(id="sidebar")
        yield sidebar
        
        yield ContentPanel(id="content")
        yield AttributionFooter(id="attribution_footer")

    def on_mount(self) -> None:
        """Fetch summary data when app mounts and set initial view."""
        # Force the initial view mounting so sidebar highlights properly
        self.run_worker(self._switch_view(self.current_view), exclusive=True)
        self.run_worker(self._fetch_summary(), name="fetch_summary", exclusive=True)
        
        # Start auto-refresh timer
        self.set_interval(1, self._tick_refresh_timer)
        
        # Background auto-updater check (Feature 50)
        self.run_worker(self._check_for_updates(), name="update_check", exclusive=False)

    async def _check_for_updates(self) -> None:
        """Check PyPI for newer versions in the background."""
        try:
            import asyncio
            from kloudkompass.core.updater import check_for_update, get_current_version
            update_available, latest = await asyncio.to_thread(check_for_update)
            if update_available and latest:
                current = get_current_version()
                alert_widget = self.query(ActiveAlerts).first()
                if alert_widget:
                    self.call_from_thread(
                        alert_widget.add_alert,
                        f"Update available: v{current} -> v{latest}. Run: pip install --upgrade kloudkompass",
                        "warning",
                    )
        except Exception:
            pass  # Never break the app for a version check

    def _tick_refresh_timer(self) -> None:
        """Decrement auto-refresh timer and update UI."""
        self.refresh_timer_seconds -= 1
        
        if self.refresh_timer_seconds <= 0:
            self.refresh_timer_seconds = 300
            self.run_worker(self.action_refresh(), exclusive=True)
            
        # Update the UI
        try:
            timer_widget = self.query_one("#refresh_timer", RefreshTimer)
            mins, secs = divmod(self.refresh_timer_seconds, 60)
            timer_widget.update(f"⏱  {mins:02d}:{secs:02d}")
        except Exception:
            pass

    async def _fetch_summary(self) -> None:
        """Fetch aggregate resource counts for the summary bar."""
        summary = self.query_one("#resource_summary", ResourceSummary)
        
        try:
            from kloudkompass.config_manager import load_config
            import asyncio
            from kloudkompass.core.provider_factory import get_compute_provider, get_storage_provider, get_database_provider
            
            config = load_config()
            region = config.get("default_region", "us-east-1")
            profile = config.get("default_profile")
            provider_name = config.get("default_provider", "aws")
            
            counts = {}
            
            # Perform data fetching concurrently to drastically cut boot times
            compute = get_compute_provider(provider_name)
            storage = get_storage_provider(provider_name)
            db = get_database_provider(provider_name)
            
            tasks = [
                asyncio.to_thread(compute.list_instances, region=region, profile=profile),
                asyncio.to_thread(storage.list_buckets, region=region, profile=profile),
                asyncio.to_thread(storage.list_volumes, region=region, profile=profile),
                asyncio.to_thread(db.list_db_instances, region=region, profile=profile)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            if not isinstance(results[0], Exception): counts["EC2"] = len(results[0])
            if not isinstance(results[1], Exception): counts["S3"] = len(results[1])
            if not isinstance(results[2], Exception): counts["EBS"] = len(results[2])
            if not isinstance(results[3], Exception): counts["RDS"] = len(results[3])
                
            summary.set_counts(counts)
            
            # Ensure the doctor widget is rendered properly
            alert_widget = self.query(ActiveAlerts).first()
            
            if alert_widget:
                self.call_from_thread(alert_widget.clear_alerts)
                
            # Perform a mini health check silently and display critical alerts
            try:
                from kloudkompass.tui.doctor import run_doctor
                from kloudkompass.core.health import ensure_cli_installed, check_credentials
                
                # Check AWS specific credentials for the summary if we're on AWS
                if provider_name == "aws":
                    _, is_valid, msg = check_credentials("aws", profile)
                    if not is_valid:
                        if alert_widget:
                            self.call_from_thread(alert_widget.add_alert, f"AWS Credentials Error: {msg}", "error")

                    def check_aws_status():
                        import urllib.request
                        import json
                        try:
                            with urllib.request.urlopen("https://status.aws.amazon.com/data.json", timeout=2) as r:
                                data = json.loads(r.read().decode())
                                for current in data.get("current", []):
                                    summary = current.get("summary", "")
                                    if "us-east-1" in current.get("service_name", "").lower() or "global" in current.get("service_name", "").lower():
                                        return f"AWS INCIDENT: {summary}"
                        except Exception:
                            pass
                        return None
                        
                    incident = await asyncio.to_thread(check_aws_status)
                    if incident and alert_widget:
                        self.call_from_thread(alert_widget.add_alert, incident, "warning")

            except Exception as e:
                # Don't break the app if health check fails, just log it 
                if alert_widget:
                    self.call_from_thread(alert_widget.add_alert, f"Failed to run health check logic: {str(e)}", "error")
            
        except Exception:
            summary.set_counts({"Summary": "Unavailable"})

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle sidebar navigation button clicks."""
        button_id = event.button.id
        if not button_id:
            return

        if button_id == "nav_settings":
            self.action_show_settings()
            return

        # Map nav button IDs to view names
        if button_id.startswith("nav_"):
            view_name = button_id.removeprefix("nav_")
            if view_name in VIEW_REGISTRY:
                await self._switch_view(view_name)

    def action_request_quit(self) -> None:
        """Show quit confirmation modal."""
        def handle_quit(confirmed: bool) -> None:
            if confirmed:
                self.notify("Closing Kloud Kompass. Stay Secure!", severity="information")
                self.exit()
        self.push_screen(QuitConfirmModal(), handle_quit)

    def action_export(self) -> None:
        """Show export modal."""
        def handle_export(path: str | None) -> None:
            if path:
                self.run_worker(self._perform_export(path), exclusive=True)
                self.notify(f"Exported to {path}", severity="information")
                
        self.push_screen(ExportModal(view_name=self.current_view, data=self._current_data), handle_export)

    def action_toggle_sidebar(self) -> None:
        """Toggle the navigation sidebar visibility."""
        sidebar = self.query(Sidebar).first()
        if sidebar:
            if sidebar.has_class("-hidden"):
                sidebar.remove_class("-hidden")
                sidebar.styles.display = "block"
            else:
                sidebar.add_class("-hidden")
                sidebar.styles.display = "none"

    def action_show_settings(self) -> None:
        """Open the settings modal."""
        def handle_settings(result) -> None:
            if result == "saved":
                self.notify("Settings saved ✓", severity="information")
        self.push_screen(SettingsModal(), handle_settings)

    async def action_show_cost(self) -> None:
        await self._switch_view("cost")

    async def action_show_compute(self) -> None:
        await self._switch_view("compute")

    async def action_show_network(self) -> None:
        await self._switch_view("network")

    async def action_show_storage(self) -> None:
        await self._switch_view("storage")

    async def action_show_iam(self) -> None:
        await self._switch_view("iam")

    async def action_show_database(self) -> None:
        await self._switch_view("database")

    async def action_show_security(self) -> None:
        await self._switch_view("security")

    async def action_show_doctor(self) -> None:
        await self._switch_view("doctor")

    async def action_refresh(self) -> None:
        """Refresh the current view by remounting it (Hits Cache if valid)."""
        await self._switch_view(self.current_view)
        self.notify("Refreshed", severity="information")

    async def action_force_refresh(self) -> None:
        """Clear local disk cache and forcefully execute live cloud API requests."""
        from kloudkompass.core.cache_manager import clear_cache
        clear_cache()
        # Reset the layout to visually wipe stale data
        await self._switch_view(self.current_view)
        # Refresh the summary counters hard
        self.run_worker(self._fetch_summary(), name="fetch_summary", exclusive=True)
        self.notify("Cache Wiped. Forced Live Sync.", severity="warning")

    def action_undo(self) -> None:
        """Stub handler overridden by actionable toasts in views."""
        self.notify("Nothing to undo.", severity="information")

    def action_cycle_focus(self) -> None:
        """Cycle focus between sidebar and content."""
        sidebar = self.query(Sidebar).first()
        if sidebar and sidebar.has_focus:
            self.query_one("#content").focus()
        else:
            if sidebar:
                sidebar.focus()

    def action_cycle_focus_reverse(self) -> None:
        self.action_cycle_focus()

    def action_show_help(self) -> None:
        """Show help modal."""
        self.push_screen(HelpModal())

    async def _switch_view(self, view_name: str) -> None:
        """
        Dynamically swap the content panel view.

        Unmounts the current view, mounts a new instance of the
        requested view class from VIEW_REGISTRY.
        """
        if view_name not in VIEW_REGISTRY:
            self.notify(f"Unknown view: {view_name}", severity="error")
            return

        self.current_view = view_name

        # Remove old view
        content = self.query_one("#content", ContentPanel)
        try:
            old_view = content.query("#active_view")
            if old_view:
                await old_view.first().remove()

            # Mount new view
            view_cls = VIEW_REGISTRY[view_name]
            self.sub_title = f"{view_name.capitalize()}"
            new_instance = view_cls(id="active_view")
            await content.mount(new_instance)
            
            # Update Breadcrumbs
            try:
                crumbs = self.query_one("#breadcrumbs", Static)
                crumbs.update(f"🏠 Dashboard > [b]{view_name.capitalize()}[/b]")
            except Exception:
                pass
                
        except Exception as e:
            self.notify(f"Dashboard Fault: {str(e)}", severity="error")
            # Mount a recovery view
            recovery = Static(f"⚠️ View Mounting Error\n\n{str(e)}\n\nCheck logs or run 'doctor'.", classes="view-error", id="active_view")
            await content.mount(recovery)

        # Update sidebar highlights
        sidebar = self.query_one("#sidebar", Sidebar)
        for button in sidebar.query(Button):
            if button.id == f"nav_{view_name}":
                button.variant = "primary"
            elif button.id != "nav_settings":
                button.variant = "default"
                
        # Persist layout to config
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("last_dashboard_view", view_name)
        except Exception:
            pass # Failsafe if TOML or filesystem errors

    def set_export_data(self, data: dict) -> None:
        """Set data for export (called by views)."""
        self._current_data = data


def launch_dashboard() -> None:
    """
    Launch the Kloud Kompass dashboard.

    This is the entry point for `kloudkompass dashboard` command.
    """
    app = KloudKompassApp()
    app.run()
