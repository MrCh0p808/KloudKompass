# kloudkompass/tui/onboarding/wizard.py
# -----------------------------------
# Textual Modal screens for the Zero-to-Hero Onboarding Engine.
# Intercepts missing CLIs and credentials, requesting permission to
# drop the user natively into the terminal using app.suspend().

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Button, SelectionList
from textual.widgets.selection_list import Selection

from kloudkompass.core.installer import get_install_command
from kloudkompass.core.auth_manager import LoginOption
from kloudkompass.dashboard.widgets.qr_widget import QRWidget
from typing import List, Dict, Optional, Any

class WizardModal(ModalScreen):
    """Base class for centered wizard popups."""
    DEFAULT_CSS = """
    WizardModal {
        align: center middle;
        background: $surface 50%;
    }
    .wizard-dialog {
        width: 60;
        height: auto;
        padding: 2 4;
        background: $boost;
        border: thick $primary;
        box-sizing: border-box;
    }
    .wizard-title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }
    .wizard-text {
        text-align: center;
        margin-bottom: 2;
    }
    .wizard-code {
        background: $surface-darken-1;
        color: $secondary;
        padding: 1;
        margin-bottom: 2;
        text-align: left;
    }
    .wizard-buttons {
        align: center middle;
        height: auto;
        margin-top: 1;
    }
    .wizard-guide {
        background: $surface;
        color: $text-muted;
        padding: 1 2;
        margin-top: 1;
        border-left: solid $accent;
    }
    .guide-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    .guide-item {
        margin-bottom: 0;
    }
    #auth_selector {
        height: 8;
        margin-bottom: 1;
        border: none;
    }
    .qr-flex-container {
        layout: horizontal;
        height: 10;
        background: $surface-darken-1;
        margin-top: 1;
        padding: 1 2;
        border: dashed $primary;
    }
    #qr_auth {
        width: 16;
        height: auto;
    }
    .qr-header {
        color: $accent;
        text-style: bold;
        margin-left: 2;
        margin-top: 1;
    }
    .qr-sub {
        color: $text-muted;
        margin-left: 2;
    }
    """

class DependencyModal(WizardModal):
    """Prompts the user to install a missing CLI tool using native OS commands."""
    
    def __init__(self, provider: str):
        super().__init__()
        self.provider = provider
        self.cmd = get_install_command(provider)

    def compose(self) -> ComposeResult:
        with Vertical(classes="wizard-dialog"):
            yield Static(f"🛠️  Missing {self.provider.upper()} Dependencies", classes="wizard-title")
            yield Static(
                f"It looks like the {self.provider.upper()} tool isn't installed on this machine yet.\n"
                "KloudKompass needs this to talk to your cloud account securely. "
                "We can run the official installer for you now. "
                "You might see a black terminal screen for a moment—don't worry, that's just us doing the heavy lifting!",
                classes="wizard-text"
            )
            
            if self.cmd:
                yield Static(f"> {self.cmd}", classes="wizard-code")
            else:
                yield Static("Manual installation required. Command not found for your OS.", classes="wizard-code")

            with Horizontal(classes="wizard-buttons"):
                if self.cmd:
                    yield Button("ACCEPT & INSTALL", variant="success", id="btn_accept")
                yield Button("CANCEL & QUIT", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_accept":
            self.dismiss(self.cmd)
        else:
            self.app.exit()


class AuthModal(WizardModal):
    """Prompts the user to select and launch a cloud authentication method."""
    
    def __init__(self, provider: str, options: List[LoginOption], qr_url: Optional[str] = None):
        super().__init__()
        self.provider = provider
        self.options = options
        self.qr_url = qr_url
        self._selected_option = next((opt for opt in options if opt.is_recommended), options[0])

    def compose(self) -> ComposeResult:
        with Vertical(classes="wizard-dialog"):
            yield Static(f"🔐 Select Login Method ({self.provider.upper()})", classes="wizard-title")
            yield Static(
                "Choose how you want to connect to your cloud account. "
                "SSO is highly recommended for security and ease of use.",
                classes="wizard-text"
            )
            
            # 1. Selection List for Auth Methods
            selections = [
                Selection(opt.name, opt.id, opt.id == self._selected_option.id)
                for opt in self.options
            ]
            yield SelectionList(*selections, id="auth_selector")
            
            # 2. Dynamic Description & Command
            yield Static(self._selected_option.description, id="auth_desc", classes="wizard-text")
            yield Static(f"> {self._selected_option.command}", id="auth_cmd_display", classes="wizard-code")
            
            if self.qr_url:
                with Horizontal(classes="qr-flex-container"):
                    yield QRWidget(self.qr_url, id="qr_auth")
                    with Vertical():
                        yield Static("📱 [b]Scan to Login[/b]", classes="qr-header")
                        yield Static("Use your phone to authorize this session.", classes="qr-sub")

            # 3. Dynamic Guide
            yield Vertical(id="guide_container", classes="wizard-guide")

            with Horizontal(classes="wizard-buttons"):
                yield Button("LAUNCH LOGIN", variant="success", id="btn_login")
                yield Button("CANCEL", variant="error", id="btn_cancel")

    def on_mount(self) -> None:
        """Initialize the guide on first mount."""
        self.query_one("#guide_container").mount_all(self._render_guide())

    def _render_guide(self):
        """Helper to yield guide items without using context managers (avoids IndexError)."""
        yield Static(f"💡 Setup Guide:", classes="guide-title")
        for item in self._selected_option.guide:
            yield Static(item, classes="guide-item")

    def on_selection_list_selected_changed(self, event: SelectionList.SelectedChanged) -> None:
        """Update the UI when the user picks a different login method."""
        if getattr(self, "_updating_selection", False):
            return

        # Handle Radio Behavior (single selection only)
        if not event.selection_list.selected:
            self._updating_selection = True
            event.selection_list.select(self._selected_option.id)
            self._updating_selection = False
            return

        if len(event.selection_list.selected) > 1:
            self._updating_selection = True
            new_id = [sid for sid in event.selection_list.selected if sid != self._selected_option.id][0]
            event.selection_list.deselect_all()
            event.selection_list.select(new_id)
            self._updating_selection = False
            selected_id = new_id
        else:
            selected_id = event.selection_list.selected[0]
        self._selected_option = next(opt for opt in self.options if opt.id == selected_id)
        
        # Update UI components
        self.query_one("#auth_desc").update(self._selected_option.description)
        self.query_one("#auth_cmd_display").update(f"> {self._selected_option.command}")
        
        # Refresh the guide container
        guide_container = self.query_one("#guide_container")
        guide_container.query("*").remove()
        guide_container.mount_all(self._render_guide())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_login":
            # Return the selected option so the app knows both command AND guide
            self.dismiss(self._selected_option)
        else:
            self.dismiss(None)


class WorkspaceModal(WizardModal):
    """Allows user to select which cloud identities map to their Tabs."""
    
    def __init__(self, provider: str, workspaces: list):
        super().__init__()
        self.provider = provider
        self.workspaces = workspaces  # list of strings or dicts

    def compose(self) -> ComposeResult:
        with Vertical(classes="wizard-dialog", id="workspace_dialog"):
            yield Static("🚀 Select Workspaces", classes="wizard-title")
            yield Static(
                "KloudKompass detected multiple environments. "
                "Select which ones you want to monitor. They will be loaded as tabs.",
                classes="wizard-text"
            )
            
            selections = []
            if self.provider == "aws":
                for profile in self.workspaces:
                    selections.append(Selection(profile, profile, profile == "default"))
            elif self.provider == "azure":
                for sub in self.workspaces:
                    name = sub.get("name", "Unknown")
                    selections.append(Selection(name, sub, sub.get("isDefault", False)))
            
            yield SelectionList(*selections, id="workspace_selector")
            
            with Horizontal(classes="wizard-buttons"):
                yield Button("MOUNT DASHBOARD", variant="success", id="btn_mount")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_mount":
            selected = self.query_one(SelectionList).selected
            self.dismiss(selected)
