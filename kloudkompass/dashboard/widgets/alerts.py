# kloudkompass/dashboard/widgets/alerts.py
# -------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# ActiveAlerts widget to show critical findings across the platform.

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static


class ActiveAlerts(Static):
    """
    Displays active alert banners for failed health checks or critical security findings.
    """

    DEFAULT_CSS = """
    ActiveAlerts {
        height: auto;
        min-height: 1;
        max-height: 5;
        background: $surface;
        border-bottom: solid $primary;
        display: none;
    }
    
    ActiveAlerts.-has-alerts {
        display: block;
    }
    
    ActiveAlerts .alert-item {
        color: $error;
        text-style: bold;
        padding-left: 2;
        padding-right: 2;
    }
    
    ActiveAlerts .alert-warning {
        color: $warning;
        text-style: bold;
        padding-left: 2;
        padding-right: 2;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._alerts = []

    def compose(self) -> ComposeResult:
        yield VerticalScroll(id="alerts_container")

    def add_alert(self, message: str, level: str = "error") -> None:
        """Add an alert to the widget."""
        self._alerts.append((message, level))
        self._render_alerts()

    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self._alerts.clear()
        self._render_alerts()

    def _render_alerts(self) -> None:
        """Render the current alerts to the container."""
        container = self.query_one("#alerts_container", VerticalScroll)
        container.remove_children()
        
        if not self._alerts:
            self.remove_class("-has-alerts")
            return
            
        self.add_class("-has-alerts")
        
        for msg, level in self._alerts:
            cls_name = "alert-item" if level == "error" else "alert-warning"
            icon = "🚨" if level == "error" else "⚠️"
            container.mount(Static(f"{icon} {msg}", classes=cls_name))
