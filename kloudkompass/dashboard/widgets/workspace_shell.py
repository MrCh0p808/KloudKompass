# kloudkompass/dashboard/widgets/workspace_shell.py
# --------------------------------------------
# The core UI shell for a Cloud account kernel.
# Encapsulates Sidebar + ContentPanel into a single isolated workspace.

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Header, LoadingIndicator, ContentSwitcher
from textual.message import Message
from textual.reactive import reactive
import dataclasses
import asyncio

from kloudkompass.dashboard.widgets.resource_summary import ResourceSummary
from kloudkompass.dashboard.widgets.alerts import ActiveAlerts
from kloudkompass.dashboard.views.cost_view import CostView
from kloudkompass.dashboard.views.compute_view import ComputeView
from kloudkompass.dashboard.views.network_view import NetworkView
from kloudkompass.dashboard.views.storage_view import StorageView
from kloudkompass.dashboard.views.iam_view import IAMView
from kloudkompass.dashboard.views.database_view import DatabaseView
from kloudkompass.dashboard.views.security_view import SecurityView
from kloudkompass.dashboard.views.doctor_view import DoctorView
from kloudkompass.core.scheduler import SmartScheduler

from kloudkompass.core.provider_factory import (
    get_cost_provider, get_compute_provider, get_network_provider,
    get_storage_provider, get_iam_provider, get_database_provider,
    get_security_provider
)

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

class RefreshTimer(Static):
    """Visual countdown timer for auto-refresh."""
    DEFAULT_CSS = "RefreshTimer { width: 100%; text-align: center; color: $text-muted; margin-top: 1; }"

class DynamicSidebar(Vertical):
    """
    Sidebar that re-composes its buttons based on provider capabilities.
    """
    DEFAULT_CSS = """
    DynamicSidebar {
        width: 20%;
        background: $surface;
        border-right: solid $primary;
        padding: 1;
    }
    DynamicSidebar Button { width: 100%; margin-bottom: 1; }
    DynamicSidebar .sidebar-title { text-align: center; text-style: bold; padding: 1; margin-bottom: 1; }
    DynamicSidebar .sidebar-divider { height: 1; margin: 1 0; }
    """

    def __init__(self, manifest: dict, brand_short: str, **kwargs):
        super().__init__(**kwargs)
        self.manifest = manifest
        self.brand_short = brand_short

    def compose(self) -> ComposeResult:
        yield Static(self.brand_short, classes="sidebar-title")
        
        # Manifest maps module_key -> {label, icon, tooltip, id}
        for key, info in self.manifest.items():
            yield Button(
                f"{info.get('icon', '')} {info.get('label', key.title())}",
                id=info.get('id', f"nav_{key}"),
                tooltip=info.get('tooltip', "")
            )
            
        yield Static("", classes="sidebar-divider")
        yield RefreshTimer("⏱  05:00", id="refresh_timer")
        yield Button("⚙️  Settings", id="nav_settings", tooltip="Configure profile and regions")


class Workspace(Horizontal):
    """
    A self-contained Cloud Management Workspace with isolated state.
    """
    manifest = reactive(dict)  # H2 FIX: factory callable, not shared mutable {}
    
    DEFAULT_CSS = """
    Workspace {
        height: 100%;
        width: 100%;
        min-height: 20;  /* Ensure it has a minimum physical presence */
        background: $surface;
        border: solid $primary-muted; /* Diagnostic border to verify it's mounted */
    }

    #workspace_switcher {
        height: 100%;
        width: 100%;
    }

    #main_ui {
        height: 100%;
        width: 100%;
        layout: horizontal;
    }

    #loader {
        width: 100%;
        height: 100%;
        content-align: center middle;
        text-style: bold italic;
        color: $accent;
        background: $surface-darken-1;
    }

    #loader LoadingIndicator {
        height: 3;
        width: auto;
        color: $accent;
    }

    Workspace #content {
        width: 1fr;
        height: 1fr;
        layout: vertical;
        background: $background;
    }

    Workspace .breadcrumb-bar {
        height: 3;
        padding: 1 2;
        background: $surface-darken-1;
        color: $text-muted;
        border-bottom: solid $primary;
        text-align: center;
    }

    Workspace #view_container {
        height: 1fr;
        width: 100%;
    }

    /* Premium Action Plate */
    Workspace .action-plate {
        dock: bottom;
        height: 5;
        background: $surface;
        border-top: tall $primary;
        layout: horizontal;
        align: center middle;
        padding: 0 2;
    }
    
    Workspace .action-plate Button {
        margin: 0 1;
        min-width: 15;
    }
    """
    
    @dataclasses.dataclass
    class SwitchView(Message):
        view_name: str
        workspace_id: str

    @dataclasses.dataclass
    class WorkspaceError(Message):
        workspace_id: str
        account_name: str
        error_msg: str

    def __init__(self, workspace_context, **kwargs):
        super().__init__(id=f"workspace_{workspace_context.id}", **kwargs)
        self.context = workspace_context
        self.current_view = workspace_context.last_view or "cost"
        self._discovery_errors: list[str] = []

    def _build_manifest(self) -> dict:
        """Aggregate manifests from all available domain providers for this cloud."""
        full_manifest = {}
        provider = self.context.provider
        
        # Domains to check
        factories = [
            get_cost_provider, get_compute_provider, get_network_provider,
            get_storage_provider, get_iam_provider, get_database_provider,
            get_security_provider
        ]
        
        for factory in factories:
            try:
                p = factory(provider)
                if hasattr(p, "get_manifest"):
                    full_manifest.update(p.get_manifest())
            except Exception as e:
                # C1 FIX: Collect errors instead of posting from background thread.
                # post_message is NOT thread-safe; messages are posted in _run_discovery.
                self._discovery_errors.append(str(e))
                continue
                
        # Always include the Doctor
        full_manifest["doctor"] = {
            "label": "🩺 Doctor", "icon": "🩺", "tooltip": "System health diagnostics", "id": "nav_doctor"
        }
        
        return full_manifest

    def compose(self) -> ComposeResult:
        with ContentSwitcher(initial="loader", id="workspace_switcher"):
            with Container(id="loader"):
                yield LoadingIndicator()
                yield Static("✨ Discovering Cloud Resources...")
            
            with Horizontal(id="main_ui"):
                from kloudkompass.tui.screens import BRAND_SHORT
                yield DynamicSidebar(self.manifest, f"{BRAND_SHORT} [{self.context.profile}]", id="sidebar")
                
                with Container(id="content"):
                    yield Static(f"🏠 Dashboard > [b]{self.current_view.capitalize()}[/b]", id="breadcrumbs", classes="breadcrumb-bar")
                    yield ResourceSummary(id="resource_summary")
                    yield ActiveAlerts(id="active_alerts")
                    yield Container(id="view_container")

    def on_mount(self) -> None:
        self.scheduler = SmartScheduler()
        self.run_worker(self.scheduler.start())
        # Start discovery worker
        self.run_worker(self._run_discovery())
        # Start auto-refresh interval (queued)
        self.set_interval(300, self.trigger_refresh)

    async def _run_discovery(self) -> None:
        """Background worker to build the manifest without blocking the UI."""
        self.manifest = await asyncio.to_thread(self._build_manifest)
        
        # C1 FIX: Safe recompose targeting only the sidebar to prevent DOM racing
        sidebar = self.query_one("#sidebar", DynamicSidebar)
        sidebar.manifest = self.manifest
        await sidebar.recompose()
        
        # Reveal the main UI
        switcher = self.query_one("#workspace_switcher", ContentSwitcher)
        switcher.current = "main_ui"
        
        # C1 FIX: Now safe to post error messages (we're back on the main thread)
        for err in self._discovery_errors:
            self.post_message(self.WorkspaceError(
                workspace_id=self.context.id,
                account_name=self.context.profile or "unknown",
                error_msg=err
            ))
        # DOM is now rebuilt with #view_container — safe to mount the initial view
        await self.switch_view(self.current_view)

    def trigger_refresh(self) -> None:
        """Queue a background refresh for this workspace."""
        self.scheduler.submit_fire_and_forget(self.switch_view, self.current_view)

    async def switch_view(self, view_name: str) -> None:
        if view_name not in VIEW_REGISTRY:
            return
            
        self.current_view = view_name
        self.context.last_view = view_name
        
        container = self.query_one("#view_container", Container)
        # Clear old
        for child in container.children:
            await child.remove()
            
        # Mount new
        view_cls = VIEW_REGISTRY[view_name]
        await container.mount(view_cls(id="active_view"))
        
        # Update breadcrumbs
        self.query_one("#breadcrumbs", Static).update(f"🏠 Dashboard > [b]{view_name.capitalize()}[/b]")
        
        # Update sidebar highlights
        sidebar = self.query_one("#sidebar", DynamicSidebar)
        for button in sidebar.query(Button):
            if button.id == f"nav_{view_name}":
                button.variant = "primary"
            elif button.id != "nav_settings":
                button.variant = "default"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if not button_id: return
        
        if button_id == "nav_settings":
            self.app.action_show_settings() # Settings remain global for now
            return
            
        if button_id.startswith("nav_"):
            view_name = button_id.removeprefix("nav_")
            await self.switch_view(view_name)

    @property
    def _current_data(self) -> dict:
        """Fetch exportable data from the active view."""
        try:
            active_view = self.query_one("#active_view")
            if hasattr(active_view, "get_export_data"):
                return active_view.get_export_data()
        except Exception:
            pass
        return {}
