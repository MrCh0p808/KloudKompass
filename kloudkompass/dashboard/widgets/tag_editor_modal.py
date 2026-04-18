from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static, Input
from textual.binding import Binding

class TagEditorModal(ModalScreen[tuple]):
    """
    Inline Tag Editor Modal that enables adding or updating
    an AWS Resource Tag in the format Key=Value.
    """

    DEFAULT_CSS = """
    TagEditorModal {
        align: center middle;
        background: $surface 50%;
    }

    #tag-dialog {
        width: 50;
        height: auto;
        padding: 1 2;
        background: $panel;
        border: solid $accent;
        content-align: center middle;
    }

    #tag-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .tag-input {
        margin: 1 0;
        width: 100%;
    }

    #tag-buttons {
        layout: horizontal;
        align: center middle;
        height: 3;
        margin-top: 1;
    }

    #tag-buttons Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, targets: list[str], **kwargs):
        super().__init__(**kwargs)
        self.targets = targets

    def compose(self) -> ComposeResult:
        with Container(id="tag-dialog"):
            yield Static(f"Edit Tags for {len(self.targets)} Resource(s)", id="tag-title")
            
            yield Input(placeholder="Tag Key (e.g. Environment)", id="tag_key", classes="tag-input")
            yield Input(placeholder="Tag Value (e.g. Production)", id="tag_value", classes="tag-input")
            
            with Container(id="tag-buttons"):
                yield Button("Cancel", variant="default", id="btn_cancel")
                yield Button("Save Tag", variant="primary", id="btn_save", disabled=True)

    def on_input_changed(self, event: Input.Changed) -> None:
        key_input = self.query_one("#tag_key", Input).value.strip()
        val_input = self.query_one("#tag_value", Input).value.strip()
        
        btn = self.query_one("#btn_save", Button)
        if len(key_input) > 0 and len(val_input) > 0:
            btn.disabled = False
        else:
            btn.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_save":
            key_input = self.query_one("#tag_key", Input).value.strip()
            val_input = self.query_one("#tag_value", Input).value.strip()
            self.dismiss((key_input, val_input))
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
