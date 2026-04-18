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
        gap: 2;
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
                f"Your machine does not have the {self.provider.upper()} CLI installed.\n"
                "KloudKompass can automatically configure this for you. "
                "This will temporarily drop you to the terminal to accept OS prompts (e.g. sudo).",
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
    """Prompts the user to launch interactive SSO authentication."""
    
    def __init__(self, provider: str, auth_cmd: str):
        super().__init__()
        self.provider = provider
        self.auth_cmd = auth_cmd

    def compose(self) -> ComposeResult:
        with Vertical(classes="wizard-dialog"):
            yield Static(f"🔐 Unauthenticated ({self.provider.upper()})", classes="wizard-title")
            yield Static(
                "KloudKompass relies on the official CLI credentials for security.\n"
                "You are currently unauthenticated or your SSO token has expired. "
                "Click below to launch an interactive login session.",
                classes="wizard-text"
            )
            yield Static(f"> {self.auth_cmd}", classes="wizard-code")

            with Horizontal(classes="wizard-buttons"):
                yield Button("LAUNCH LOGIN", variant="success", id="btn_login")
                yield Button("CANCEL", variant="error", id="btn_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_login":
            self.dismiss(self.auth_cmd)
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
