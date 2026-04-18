from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Input, ProgressBar
from textual.binding import Binding

class SafeDeleteModal(ModalScreen[bool]):
    """
    Safe Deletion Modal that requires typing the precise target
    ID or "confirm" for batch operations to prevent accidental terminations.
    """

    DEFAULT_CSS = """
    SafeDeleteModal {
        align: center middle;
        background: $surface 50%;
    }

    #dialog {
        width: 60;
        height: auto;
        padding: 1 2;
        background: $panel;
        border: solid $error;
        content-align: center middle;
    }

    #dialog-title {
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    #dialog-input {
        margin: 1 0;
        width: 100%;
    }

    #dialog-buttons {
        layout: horizontal;
        align: center middle;
        height: 3;
        margin-top: 1;
    }

    #dialog-buttons Button {
        margin: 0 1;
    }

    #progressBar {
        margin: 1 0;
        width: 100%;
        display: none;
    }

    #progressBar.active {
        display: block;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, target_ids: list[str], **kwargs):
        super().__init__(**kwargs)
        self.target_ids = target_ids
        # If multiple targets, type 'confirm', else type the exact ID
        self.expected_input = "confirm" if len(target_ids) > 1 else target_ids[0]

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Static("⚠ DANGER: IRREVERSIBLE ACTION ⚠", id="dialog-title")
            
            if len(self.target_ids) > 1:
                yield Static(f"You are about to TERMINATE {len(self.target_ids)} instances!\nTo proceed, please explicitly type [bold error]confirm[/] below:")
            else:
                yield Static(f"You are about to TERMINATE instance [bold error]{self.target_ids[0]}[/]!\nTo proceed, please explicitly type the exact instance ID below:")
                
            yield Input(placeholder=self.expected_input, id="confirm_input")
            
            yield ProgressBar(id="progressBar", show_eta=False)
            
            with Container(id="dialog-buttons"):
                yield Button("Cancel", variant="primary", id="btn_cancel")
                yield Button("Terminate", variant="error", id="btn_terminate", disabled=True)

    def on_input_changed(self, event: Input.Changed) -> None:
        btn = self.query_one("#btn_terminate", Button)
        if event.value.strip() == self.expected_input:
            btn.disabled = False
        else:
            btn.disabled = True

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_terminate":
            # Show progress bar and disable inputs
            pb = self.query_one("#progressBar", ProgressBar)
            pb.add_class("active")
            pb.update(total=100)
            
            inp = self.query_one("#confirm_input", Input)
            inp.disabled = True
            self.query_one("#btn_terminate", Button).disabled = True
            self.query_one("#btn_cancel", Button).disabled = True
            
            # Simulate a brief "action sequence" to provide UX feedback
            import asyncio
            for i in range(10):
                pb.advance(10)
                await asyncio.sleep(0.05)
                
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)
