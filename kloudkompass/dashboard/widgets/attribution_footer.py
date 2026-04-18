# kloudkompass/dashboard/widgets/attribution_footer.py
# ---------------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Custom footer widget for Textual dashboard with persistent legal attribution.
# This is the single source of truth for dashboard attribution rendering.

from textual.widgets import Static

# Import from centralized source - footer.py has the constants
from kloudkompass.tui.footer import ATTRIBUTION_FULL


class AttributionFooter(Static):
    """
    Persistent attribution footer for Textual dashboard.
    
    This widget replaces Textual's built-in Footer to ensure legal
    attribution is always visible. It renders once and persists
    across all dashboard navigation.
    
    Invariants:
        - Rendered once at compose time
        - Never re-instantiated by screens
        - Docked at bottom persistently
        - Stateless - no internal state changes
    """
    
    DEFAULT_CSS = """
    AttributionFooter {
        dock: bottom;
        height: 2;
        background: $surface;
        color: $text-muted;
        text-align: center;
        padding: 0 1;
        border-top: solid $primary-darken-2;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__(ATTRIBUTION_FULL, **kwargs)
    
    def on_mount(self) -> None:
        """
        Mount handler - attribution is set at init, nothing to do here.
        
        This ensures the widget is truly stateless after initialization.
        """
        pass
