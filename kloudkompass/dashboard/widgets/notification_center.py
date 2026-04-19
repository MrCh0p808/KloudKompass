# kloudkompass/dashboard/widgets/notification_center.py
# -----------------------------------------------
# Decision-based notification center for the Management OS.
# Handles critical background errors through Switch-Attention modals.

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Button, Footer
from textual.screen import ModalScreen

class SystemAttentionModal(ModalScreen):
    """
    A decision modal that pops up when a background kernel needs attention.
    """
    
    DEFAULT_CSS = """
    SystemAttentionModal {
        align: center middle;
    }

    #attention_container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $error;
        padding: 1 2;
    }

    #attention_title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    #attention_msg {
        margin-bottom: 1;
    }

    #attention_buttons {
        align: center middle;
        height: 3;
    }
    
    #attention_buttons Button {
        margin: 0 1;
    }
    """

    def __init__(self, workspace_id: str, account_name: str, error_msg: str, **kwargs):
        super().__init__(**kwargs)
        self.workspace_id = workspace_id
        self.account_name = account_name
        self.error_msg = error_msg

    def compose(self) -> ComposeResult:
        with Vertical(id="attention_container"):
            yield Static(f"⚠️ SYSTEM ATTENTION REQUIRED", id="attention_title")
            yield Static(f"Account: [b]{self.account_name}[/b]", id="attention_account")
            yield Static(f"Error: {self.error_msg}", id="attention_msg")
            
            with Horizontal(id="attention_buttons"):
                yield Button("Jump to Workspace", variant="primary", id="btn_jump")
                yield Button("Re-Login", variant="warning", id="btn_login")
                yield Button("Dismiss", variant="default", id="btn_dismiss")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_jump":
            self.dismiss(("jump", self.workspace_id))
        elif event.button.id == "btn_login":
            self.dismiss(("login", self.workspace_id))
        else:
            self.dismiss(None)
