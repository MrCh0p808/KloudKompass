# kloudkompass/dashboard/widgets/help_modal.py
# -------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Help modal for dashboard mode.
# Phase 2.6: Shows full keybinding reference.

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical
from textual.widgets import Static, Button

from kloudkompass.tui.screens import BRAND_TITLE, BRAND_SHORT
from kloudkompass.tui.footer import ATTRIBUTION_SHORT


HELP_TEXT = f"""
╔══════════════════════════════════════════╗
║  {BRAND_SHORT} — Dashboard Help          ║
╠══════════════════════════════════════════╣
║                                          ║
║  Navigation                              ║
║  ──────────                              ║
║  C       Cost Analysis                   ║
║  I       Inventory (coming soon)         ║
║  S       Security  (coming soon)         ║
║  D       Doctor    (health checks)       ║
║                                          ║
║  Actions                                 ║
║  ────────                                ║
║  E       Export current view             ║
║  R       Refresh data                    ║
║  ?       Show this help                  ║
║  Q       Quit (with confirmation)        ║
║                                          ║
║  Export Formats                           ║
║  ──────────────                           ║
║  CSV      Comma-separated values         ║
║  JSON     Machine-readable format        ║
║  Markdown Readable tables                ║
║                                          ║
║  {ATTRIBUTION_SHORT}                     ║
╚══════════════════════════════════════════╝
""".strip()


class HelpModal(ModalScreen[None]):
    """
    Help modal showing all keybindings and features.
    
    Phase 2.6: Replaces the basic notification with a proper
    modal that shows full navigation and action reference.
    """
    
    DEFAULT_CSS = """
    HelpModal {
        align: center middle;
    }
    
    HelpModal > Vertical {
        width: 50%;
        min-width: 45;
        max-width: 80;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $accent;
        padding: 1 2;
    }
    
    HelpModal .help-text {
        margin-bottom: 1;
    }
    
    HelpModal Button {
        width: 100%;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        ("escape", "dismiss_help", "Close"),
        ("?", "dismiss_help", "Close"),
    ]
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(HELP_TEXT, classes="help-text")
            yield Button("Close  [Esc/?]", variant="primary", id="help_close")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "help_close":
            self.dismiss(None)
    
    def action_dismiss_help(self) -> None:
        self.dismiss(None)
