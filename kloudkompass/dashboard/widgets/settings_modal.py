# kloudkompass/dashboard/widgets/settings_modal.py
# ------------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Settings modal for configuring provider, region, and profile.

from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Static, Button, Input, Select


# Common AWS regions
REGION_OPTIONS = [
    ("US East (N. Virginia)", "us-east-1"),
    ("US East (Ohio)", "us-east-2"),
    ("US West (N. California)", "us-west-1"),
    ("US West (Oregon)", "us-west-2"),
    ("EU (Ireland)", "eu-west-1"),
    ("EU (Frankfurt)", "eu-central-1"),
    ("Asia Pacific (Mumbai)", "ap-south-1"),
    ("Asia Pacific (Singapore)", "ap-southeast-1"),
]

PROVIDER_OPTIONS = [
    ("Amazon Web Services", "aws"),
    ("Google Cloud Platform", "gcp"),
    ("Microsoft Azure", "azure"),
]


class SettingsModal(ModalScreen):
    """
    Settings modal — configure provider, region, and profile.

    Changes persist to ~/.kloudkompass/config.toml and update
    the active session.
    """

    DEFAULT_CSS = """
    SettingsModal {
        align: center middle;
    }

    SettingsModal > Vertical {
        width: 60%;
        min-width: 45;
        max-width: 80;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    SettingsModal .modal-title {
        text-align: center;
        text-style: bold;
        padding: 1;
    }

    SettingsModal .field-label {
        margin-top: 1;
        text-style: bold;
    }

    SettingsModal Input {
        margin-bottom: 1;
    }

    SettingsModal Select {
        margin-bottom: 1;
    }

    SettingsModal .button-row {
        margin-top: 1;
        height: 3;
        align: center middle;
    }

    SettingsModal .button-row Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        # Prevent Textual crash if config has invalid/custom values not in defaults
        provider_val = self._current_provider()
        provider_opts = list(PROVIDER_OPTIONS)
        if provider_val and provider_val not in [p[1] for p in provider_opts]:
            provider_opts.append((provider_val, provider_val))

        region_val = self._current_region()
        region_opts = list(REGION_OPTIONS)
        if region_val and region_val not in [r[1] for r in region_opts]:
            region_opts.append((region_val, region_val))

        with Vertical():
            yield Static("⚙️  Settings", classes="modal-title")

            yield Static("Cloud Provider:", classes="field-label")
            yield Select(
                provider_opts,
                id="select_provider",
                value=provider_val,
            )

            yield Static("Region:", classes="field-label")
            yield Select(
                region_opts,
                id="select_region",
                value=region_val,
                allow_blank=True,
            )

            yield Static("AWS Profile (optional):", classes="field-label")
            yield Input(
                placeholder="default",
                id="input_profile",
                value=self._current_profile(),
            )

            with Horizontal(classes="button-row"):
                yield Button("Save", id="btn_save", variant="primary")
                yield Button("Cancel", id="btn_cancel")

    def _current_provider(self) -> str:
        try:
            from kloudkompass.config_manager import load_config
            return load_config().get("default_provider", "aws")
        except Exception:
            return "aws"

    def _current_region(self) -> str:
        try:
            from kloudkompass.config_manager import load_config
            return load_config().get("default_region", "us-east-1")
        except Exception:
            return "us-east-1"

    def _current_profile(self) -> str:
        try:
            from kloudkompass.config_manager import load_config
            return load_config().get("default_profile", "")
        except Exception:
            return ""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_cancel":
            self.dismiss(None)
        elif event.button.id == "btn_save":
            self._save_settings()

    def _save_settings(self) -> None:
        try:
            from kloudkompass.config_manager import load_config, save_config
            from kloudkompass.tui.session import update_session, get_session

            provider_select = self.query_one("#select_provider", Select)
            region_select = self.query_one("#select_region", Select)
            profile_input = self.query_one("#input_profile", Input)

            provider = str(provider_select.value) if provider_select.value else "aws"
            region = str(region_select.value) if region_select.value else ""
            profile = profile_input.value.strip() or None

            # Update config
            config = load_config()
            config["default_provider"] = provider
            if region:
                config["default_region"] = region
            if profile:
                config["default_profile"] = profile
            save_config(config)

            # Update live session
            session = get_session()
            new_session = session.with_provider(provider)
            if region:
                new_session = new_session.with_region(region)
            if profile:
                new_session = new_session.with_profile(profile)
            update_session(new_session)

            self.dismiss("saved")

        except Exception as e:
            self.notify(f"Save failed: {e}", severity="error")
