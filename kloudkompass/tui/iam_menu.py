# kloudkompass/tui/iam_menu.py
# ----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# IAM (Identity & Access Management) viewer screen.

from typing import Optional

from kloudkompass.tui.screens import Screen
from kloudkompass.tui.session import update_session
from kloudkompass.tui.provider_setup import ensure_provider_configured
from kloudkompass.core.provider_factory import get_iam_provider
from kloudkompass.core.exceptions import KloudKompassError


IAM_OPTIONS = [
    ("1", "List IAM Users"),
    ("2", "List IAM Roles"),
    ("3", "List Customer Policies"),
    ("4", "Find Users Without MFA"),
]


class IAMMenuScreen(Screen):
    """IAM resources viewer — Users, Roles, Policies."""

    title = "IAM Resources"

    def render(self) -> None:
        provider = self.session.provider or "aws"
        print(f"  Provider: {provider.upper()}")
        print()
        for key, label in IAM_OPTIONS:
            print(f"  {key}. {label}")
        self.print_nav_hint()

    def handle_input(self) -> Optional[Screen]:
        if not self.session.provider:
            update_session(self.session.with_provider("aws"))

        result = self.get_input()
        if result.is_quit:
            return "exit"
        if result.is_back:
            return "back"

        choice = result.raw
        if choice == "1":
            self._list_users()
        elif choice == "2":
            self._list_roles()
        elif choice == "3":
            self._list_policies()
        elif choice == "4":
            self._find_no_mfa()
        else:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")
        return None

    def _list_users(self) -> None:
        provider_name = self.session.provider or "aws"
        gate = ensure_provider_configured(provider_name)
        if not gate.success:
            self.print_error(gate.message)
            input("Press Enter to continue...")
            return

        print("\nFetching IAM users (this may take a moment)...")
        try:
            provider = get_iam_provider(provider_name)
            users = provider.list_users(profile=self.session.profile)
            if not users:
                print("\nNo IAM users found.")
            else:
                print(f"\nFound {len(users)} user(s):\n")
                print(f"  {'Username':<24} {'MFA':<5} {'Keys':<5} {'Last Login':<22} {'Created'}")
                print(f"  {'─'*24} {'─'*5} {'─'*5} {'─'*22} {'─'*22}")
                for u in users:
                    mfa = "✓" if u.mfa_enabled else "✗"
                    last = u.last_login[:19] if u.last_login and u.last_login != "Never" else "Never"
                    created = u.create_date[:19] if u.create_date else "—"
                    print(f"  {u.user_name:<24} {mfa:<5} {u.access_keys:<5} {last:<22} {created}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _list_roles(self) -> None:
        provider_name = self.session.provider or "aws"
        gate = ensure_provider_configured(provider_name)
        if not gate.success:
            self.print_error(gate.message)
            input("Press Enter to continue...")
            return

        print("\nFetching IAM roles...")
        try:
            provider = get_iam_provider(provider_name)
            roles = provider.list_roles(profile=self.session.profile)
            if not roles:
                print("\nNo IAM roles found.")
            else:
                print(f"\nFound {len(roles)} role(s):\n")
                print(f"  {'Role Name':<40} {'Description':<40} {'Created'}")
                print(f"  {'─'*40} {'─'*40} {'─'*22}")
                for r in roles:
                    desc = (r.description[:37] + "...") if len(r.description) > 40 else r.description
                    created = r.create_date[:19] if r.create_date else "—"
                    print(f"  {r.role_name[:40]:<40} {desc:<40} {created}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _list_policies(self) -> None:
        provider_name = self.session.provider or "aws"
        gate = ensure_provider_configured(provider_name)
        if not gate.success:
            self.print_error(gate.message)
            input("Press Enter to continue...")
            return

        print("\nFetching customer-managed IAM policies...")
        try:
            provider = get_iam_provider(provider_name)
            policies = provider.list_policies(scope="Local", profile=self.session.profile)
            if not policies:
                print("\nNo customer-managed policies found.")
            else:
                print(f"\nFound {len(policies)} policy(ies):\n")
                print(f"  {'Policy Name':<40} {'Attachments':<13} {'Created'}")
                print(f"  {'─'*40} {'─'*13} {'─'*22}")
                for p in policies:
                    created = p.create_date[:19] if p.create_date else "—"
                    print(f"  {p.policy_name[:40]:<40} {p.attachment_count:<13} {created}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _find_no_mfa(self) -> None:
        provider_name = self.session.provider or "aws"
        gate = ensure_provider_configured(provider_name)
        if not gate.success:
            self.print_error(gate.message)
            input("Press Enter to continue...")
            return

        print("\nChecking IAM users for MFA status...")
        try:
            provider = get_iam_provider(provider_name)
            users = provider.list_users(profile=self.session.profile)
            no_mfa = provider.find_users_without_mfa(users)
            if not no_mfa:
                print("\n✓ All users have MFA enabled. Well done!")
            else:
                print(f"\n⚠ Found {len(no_mfa)} user(s) WITHOUT MFA:\n")
                print(f"  {'Username':<24} {'Keys':<5} {'Last Login'}")
                print(f"  {'─'*24} {'─'*5} {'─'*22}")
                for u in no_mfa:
                    last = u.last_login[:19] if u.last_login and u.last_login != "Never" else "Never"
                    print(f"  {u.user_name:<24} {u.access_keys:<5} {last}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")
