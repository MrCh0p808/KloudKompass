# bashcloud/dashboard/app.py
# ---------------------------
# the main Textual application This is the entry point
# for dashboard mode with full keyboard navigation and live updates.

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem, Label
from textual.binding import Binding

from bashcloud.dashboard.views.cost_view import CostView


class Sidebar(Vertical):
    """
    Navigation sidebar.
    
    Contains buttons for switching between different views.
    """
    
    DEFAULT_CSS = """
    Sidebar {
        width: 20;
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
    """
    
    def compose(self) -> ComposeResult:
        yield Static("BashCloud", classes="sidebar-title")
        yield Button("Cost", id="nav_cost", variant="primary")
        yield Button("Inventory", id="nav_inventory")
        yield Button("Security", id="nav_security")
        yield Button("Doctor", id="nav_doctor")


class ContentPanel(Container):
    """
    Main content panel that switches between views.
    """
    
    DEFAULT_CSS = """
    ContentPanel {
        width: 1fr;
        height: 100%;
    }
    """
    
    def compose(self) -> ComposeResult:
        # Start with cost view
        yield CostView(id="cost_view")


class BashCloudApp(App):
    """
    Main BashCloud dashboard application.
    
    A full-featured terminal dashboard for cloud cost analysis.
    Uses Textual for rich UI, keyboard navigation, and async operations.
    """
    
    TITLE = "BashCloud Dashboard"
    SUB_TITLE = "Cloud Cost Analysis"
    
    CSS = """
    Screen {
        layout: horizontal;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "show_cost", "Cost"),
        Binding("i", "show_inventory", "Inventory"),
        Binding("s", "show_security", "Security"),
        Binding("d", "show_doctor", "Doctor"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def compose(self) -> ComposeResult:
        """Build the main application layout."""
        yield Header()
        yield Sidebar(id="sidebar")
        yield ContentPanel(id="content")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle sidebar navigation button clicks."""
        button_id = event.button.id
        
        if button_id == "nav_cost":
            self.action_show_cost()
        elif button_id == "nav_inventory":
            self.action_show_inventory()
        elif button_id == "nav_security":
            self.action_show_security()
        elif button_id == "nav_doctor":
            self.action_show_doctor()
    
    def action_show_cost(self) -> None:
        """Switch to cost view."""
        self._switch_view("cost")
    
    def action_show_inventory(self) -> None:
        """Switch to inventory view."""
        self.notify("Inventory view not yet implemented", severity="warning")
    
    def action_show_security(self) -> None:
        """Switch to security view."""
        self.notify("Security view not yet implemented", severity="warning")
    
    def action_show_doctor(self) -> None:
        """Run doctor checks."""
        from bashcloud.tui.doctor import run_doctor
        
        results = run_doctor()
        passed = sum(1 for _, _, p in results if p)
        failed = len(results) - passed
        
        if failed == 0:
            self.notify(f"All {passed} checks passed", severity="information")
        else:
            self.notify(f"{failed} checks failed", severity="warning")
    
    def action_refresh(self) -> None:
        """Refresh current view."""
        self.notify("Refreshing...", severity="information")
    
    def _switch_view(self, view_name: str) -> None:
        """
        Switch the content panel to a different view.
        
        For now only cost view is implemented.
        """
        # Update sidebar button states
        sidebar = self.query_one("#sidebar", Sidebar)
        for button in sidebar.query(Button):
            if button.id == f"nav_{view_name}":
                button.variant = "primary"
            else:
                button.variant = "default"


def launch_dashboard() -> None:
    """
    Launch the BashCloud dashboard.
    
    This is the entry point for `bashcloud dashboard` command.
    """
    app = BashCloudApp()
    app.run()
