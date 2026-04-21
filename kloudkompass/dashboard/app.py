# kloudkompass/dashboard/app.py
# ---------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Main Textual application for the Multi-Kernel Management OS.
# Orchestrates multiple workspace kernels with isolated state.

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Static, Button, TabbedContent, TabPane
from textual.binding import Binding
from textual.command import Provider, Hit

from kloudkompass.dashboard.widgets.attribution_footer import AttributionFooter
from kloudkompass.dashboard.widgets.quit_modal import QuitConfirmModal
from kloudkompass.dashboard.widgets.export_modal import ExportModal
from kloudkompass.dashboard.widgets.help_modal import HelpModal
from kloudkompass.dashboard.widgets.settings_modal import SettingsModal
from kloudkompass.tui.screens import BRAND_TITLE, BRAND_SHORT, BRAND_BANNER

from kloudkompass.dashboard.widgets.workspace_shell import Workspace
from kloudkompass.dashboard.widgets.notification_center import SystemAttentionModal
from kloudkompass.core.workspace_registry import WorkspaceRegistry, WorkspaceContext
from kloudkompass.core.auth_manager import get_login_options
from kloudkompass.tui.onboarding.wizard import AuthModal


class KloudKompassApp(App):
    """
    The Orchestrator for the KloudKompass Management OS.
    """

    TITLE = BRAND_TITLE
    SUB_TITLE = "Management OS"
    
    ENABLE_COMMAND_PALETTE = True

    CSS = """
    Screen {
        height: 100vh;
        width: 100vw;
        background: $background;
    }

    .guide-item {
        margin-bottom: 0;
    }
    #auth_selector {
        height: 6;
        margin-bottom: 1;
        border: none;
    }
    
    TabbedContent {
        height: 1fr;
    }
    
    TabbedContent TabPane {
        height: 100%;
        layout: vertical;
        padding: 0;
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
    
    /* Global Neuromorphic Palette */
    Button:hover {
        background: $accent;
        color: $text-accent;
        text-style: reverse;
        transition: background 250ms;
    }
    """

    BINDINGS = [
        Binding("q", "request_quit", "Quit", show=True),
        Binding("e", "export", "Export", show=True),
        Binding("r", "refresh", "Refresh"),
        Binding("f5", "force_refresh", "Force Refresh"),
        Binding("d", "toggle_dark", "Toggle Dark/Light Mode"),
        Binding("ctrl+k", "command_palette", "Command Palette"),
        Binding("?", "show_help", "Help"),
        Binding("tab", "cycle_focus", "Cycle Focus", show=False),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.registry = WorkspaceRegistry()
        self._current_data = {}

    def compose(self) -> ComposeResult:
        """Build the main OS layout."""
        yield Header()
        banner = Static(BRAND_BANNER, id="app_banner")
        banner.markup = False
        yield banner
        
        with TabbedContent(id="workspaces_container"):
            # Workspaces will be mounted dynamically
            pass
            
        yield AttributionFooter(id="attribution_footer")

    def on_mount(self) -> None:
        """Dashboard entry point. Triggers multi-kernel discovery."""
        self.run_worker(self._run_os_initialization(), exclusive=True)

    async def _run_os_initialization(self) -> None:
        """
        Discover identities, check health, and mount active workspace kernels.
        """
        from kloudkompass.tui.onboarding.wizard import DependencyModal, WorkspaceModal
        from kloudkompass.core.health import check_credentials
        
        # 1. Discover all identities on the system
        discovered = self.registry.discover_all()
        for ws in discovered:
            self.registry.add_workspace(ws)
            
        active = self.registry.get_active_workspaces()
        
        # 2. If no active workspaces, run onboarding for the default provider
        if not active:
            from kloudkompass.config_manager import load_config
            config = load_config()
            provider = config.get("default_provider", "aws").lower()
            
            # Basic dependency/auth check for the "Gateway" account
            is_valid, _ = check_credentials(provider)
            if not is_valid:
                options = get_login_options(provider)
                if options:
                    selected_opt = await self.push_screen_wait(AuthModal(provider, options))
                    if selected_opt:
                        await self.execute_interactive_command(selected_opt.command, guide=selected_opt.guide)
                        # Re-discover after login
                        for ws in self.registry.discover_all():
                            self.registry.add_workspace(ws)
            
            # Update active list after onboarding
            active = self.registry.get_active_workspaces()
            if not active:
                # If still nothing active (first run), pick the first discovered
                all_ws = list(self.registry.workspaces.values())
                if all_ws:
                    self.registry.activate_workspace(all_ws[0].id)
                    active = [all_ws[0]]
        
        # 3. Mount all active workspaces into the TabbedContent
        tab_container = self.query_one("#workspaces_container", TabbedContent)
        for ws_ctx in active:
            label = f"{ws_ctx.provider.upper()}: {ws_ctx.profile}"
            await tab_container.add_pane(
                TabPane(label, Workspace(ws_ctx), id=f"tab_{ws_ctx.id}")
            )

    async def execute_interactive_command(self, cmd: str, guide: list[str] = None) -> None:
        """Suspend the app, run a native shell command, and resume."""
        import subprocess
        import shlex  # C3 FIX: safe command splitting
        with self.suspend():
            print("\033[2J\033[H") # Clear terminal
            print("=" * 80)
            print(f" KloudKompass | Sub-process Shell: {cmd}")
            print("=" * 80)
            if guide:
                print("\n".join(guide))
                print("-" * 80)
            print(f"\n[Executing...] {cmd}\n")
            
            # C3 FIX: shell=False prevents command injection via semicolons/pipes
            subprocess.run(shlex.split(cmd))
            
            print("\n" + "=" * 80)
            print(" [DONE] Process finished. Press Enter to return to Dashboard UI...")
            print("=" * 80)
            input()

    def action_request_quit(self) -> None:
        def handle_quit(confirmed: bool) -> None:
            if confirmed:
                self.registry.save_to_config()
                self.exit()
        self.push_screen(QuitConfirmModal(), handle_quit)

    def action_show_settings(self) -> None:
        self.push_screen(SettingsModal())

    def action_show_help(self) -> None:
        self.push_screen(HelpModal())

    def action_export(self) -> None:
        # Export needs to query the active workspace
        tab_container = self.query_one("#workspaces_container", TabbedContent)
        active_tab = tab_container.active
        if active_tab:
            workspace = self.query_one(f"#{active_tab}", TabPane).query_one(Workspace)
            self.push_screen(ExportModal(view_name=workspace.current_view, data=workspace._current_data))

    async def on_workspace_workspace_error(self, message: Workspace.WorkspaceError) -> None:
        """Handle background errors by popping the decision modal."""
        async def handle_attention(result):
            if not result: return
            action, ws_id = result
            if action == "jump":
                self.query_one("#workspaces_container", TabbedContent).active = f"tab_{ws_id}"
            elif action == "login":
                # Trigger auth flow for this specific workspace
                ws_ctx = self.registry.workspaces.get(ws_id)
                if ws_ctx:
                    options = get_login_options(ws_ctx.provider)
                    if options:
                        selected_opt = await self.push_screen_wait(AuthModal(ws_ctx.provider, options))
                        if selected_opt:
                            await self.execute_interactive_command(selected_opt.command, guide=selected_opt.guide)
                
        self.push_screen(
            SystemAttentionModal(message.workspace_id, message.account_name, message.error_msg),
            lambda result: self.run_worker(handle_attention(result))
        )


def launch_dashboard() -> None:
    app = KloudKompassApp()
    app.run()
