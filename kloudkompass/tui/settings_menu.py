# kloudkompass/tui/settings_menu.py
# ---------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Settings screen for editing configuration defaults.

from typing import Optional

from kloudkompass.tui.screens import Screen
from kloudkompass.tui.session import update_session
from kloudkompass.config_manager import (
    load_config,
    get_config_value,
    set_config_value,
)


SETTINGS_OPTIONS = [
    ("1", "Set Default Provider"),
    ("2", "Set Default Region"),
    ("3", "Set Default Profile"),
    ("4", "View Current Settings"),
]


class SettingsMenuScreen(Screen):
    """Settings editor for Kloud Kompass configuration."""

    title = "Settings"

    def render(self) -> None:
        print("  Manage your Kloud Kompass defaults and preferences.")
        print()
        for key, label in SETTINGS_OPTIONS:
            print(f"  {key}. {label}")
        self.print_nav_hint()

    def handle_input(self) -> Optional[Screen]:
        result = self.get_input()
        if result.is_quit:
            return "exit"
        if result.is_back:
            return "back"

        choice = result.raw
        if choice == "1":
            self._set_default_provider()
        elif choice == "2":
            self._set_default_region()
        elif choice == "3":
            self._set_default_profile()
        elif choice == "4":
            self._view_settings()
        else:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")
        return None

    def _set_default_provider(self) -> None:
        print("\nAvailable providers: aws, azure, gcp")
        result = self.get_input("Enter default provider [aws]: ")
        if result.is_quit or result.is_back:
            return

        provider = result.raw.strip().lower() or "aws"
        if provider not in ("aws", "azure", "gcp"):
            print(f"\n  Invalid provider: {provider}")
            input("Press Enter to continue...")
            return

        try:
            set_config_value("default_provider", provider)
            update_session(self.session.with_provider(provider))
            print(f"\n  ✓ Default provider set to: {provider}")
        except Exception as e:
            self.print_error(f"Failed to save setting: {e}")
        input("Press Enter to continue...")

    def _set_default_region(self) -> None:
        current = get_config_value("default_region")
        result = self.get_input(f"Enter default region [{current or 'us-east-1'}]: ")
        if result.is_quit or result.is_back:
            return

        region = result.raw.strip() or current or "us-east-1"
        try:
            set_config_value("default_region", region)
            update_session(self.session.with_region(region))
            print(f"\n  ✓ Default region set to: {region}")
        except Exception as e:
            self.print_error(f"Failed to save setting: {e}")
        input("Press Enter to continue...")

    def _set_default_profile(self) -> None:
        current = self.session.profile
        result = self.get_input(f"Enter default profile [{current or 'default'}]: ")
        if result.is_quit or result.is_back:
            return

        profile = result.raw.strip() or current or "default"
        try:
            set_config_value("default_profile", profile)
            update_session(self.session.with_profile(profile))
            print(f"\n  ✓ Default profile set to: {profile}")
        except Exception as e:
            self.print_error(f"Failed to save setting: {e}")
        input("Press Enter to continue...")

    def _view_settings(self) -> None:
        print(f"\n  Current Settings:")
        print(f"  {'─'*40}")
        config = load_config()
        print(f"  Default Provider:  {config.get('default_provider', 'aws')}")
        print(f"  Default Region:    {config.get('default_region', 'us-east-1')}")
        print(f"  Default Profile:   {config.get('default_profile', 'default')}")
        print(f"  Debug Mode:        {config.get('debug', False)}")
        print()
        input("Press Enter to continue...")
