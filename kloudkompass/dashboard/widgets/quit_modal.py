# kloudkompass/dashboard/widgets/quit_modal.py
# ------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Quit confirmation modal for dashboard - matches TUI behavior.

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Horizontal
from textual.widgets import Button, Static


class QuitConfirmModal(ModalScreen[bool]):
    """
    Modal dialog for quit confirmation.
    
    Phase 2.6: Matches TUI quit confirmation behavior.
    Default is No (don't quit) for safety.
    """
    
    DEFAULT_CSS = """
    QuitConfirmModal {
        align: center middle;
    }
    
    QuitConfirmModal > Vertical {
        width: 40%;
        min-width: 40;
        max-width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }
    
    QuitConfirmModal Static {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    
    QuitConfirmModal .title {
        text-style: bold;
    }
    
    QuitConfirmModal Horizontal {
        width: 100%;
        height: 3;
        align: center middle;
    }
    
    QuitConfirmModal Button {
        margin: 0 2;
    }
    """
    
    BINDINGS = [
        ("y", "confirm_yes", "Yes"),
        ("n", "confirm_no", "No"),
        ("escape", "confirm_no", "Cancel"),
    ]
    
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Quit Kloud Kompass?", classes="title")
            yield Static("")
            yield Static("Do you want to quit?")
            yield Static("")
            with Horizontal():
                yield Button("No", id="btn_no", variant="primary")
                yield Button("Yes", id="btn_yes", variant="error")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "btn_yes":
            self.dismiss(True)
        else:
            self.dismiss(False)
    
    def action_confirm_yes(self) -> None:
        """Confirm quit."""
        self.dismiss(True)
    
    def action_confirm_no(self) -> None:
        """Cancel quit."""
        self.dismiss(False)
