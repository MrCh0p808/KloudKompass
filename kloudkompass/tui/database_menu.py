# kloudkompass/tui/database_menu.py
# ---------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Database (RDS/DynamoDB) viewer screen.

from typing import Optional

from kloudkompass.tui.screens import Screen
from kloudkompass.tui.session import update_session, get_session
from kloudkompass.tui.provider_setup import ensure_provider_configured
from kloudkompass.tui.prompts import ensure_region_configured
from kloudkompass.core.provider_factory import get_database_provider
from kloudkompass.core.exceptions import KloudKompassError


DB_OPTIONS = [
    ("1", "List RDS Instances"),
    ("2", "List DynamoDB Tables"),
    ("3", "Find Publicly Accessible DBs"),
]


class DatabaseMenuScreen(Screen):
    """Database resources viewer — RDS and DynamoDB."""

    title = "Database Resources (RDS/DynamoDB)"

    def render(self) -> None:
        provider = self.session.provider or "aws"
        print(f"  Provider: {provider.upper()}")
        print()
        for key, label in DB_OPTIONS:
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
            self._list_rds()
        elif choice == "2":
            self._list_dynamodb()
        elif choice == "3":
            self._find_public_dbs()
        else:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")
        return None

    def _list_rds(self) -> None:
        provider_name = self.session.provider or "aws"
        gate = ensure_provider_configured(provider_name)
        if not gate.success:
            self.print_error(gate.error)
            input("Press Enter to continue...")
            return

        region_result = ensure_region_configured(self.session)
        if not region_result.success:
            self.print_error(region_result.message or "Region required.")
            input("Press Enter to continue...")
            return
        s = get_session()

        print("\nFetching RDS instances...")
        try:
            provider = get_database_provider(provider_name)
            instances = provider.list_db_instances(
                region=s.region,
                profile=s.profile,
            )
            if not instances:
                print("\nNo RDS instances found.")
            else:
                print(f"\nFound {len(instances)} RDS instance(s):\n")
                print(f"  {'DB ID':<28} {'Engine':<15} {'Class':<15} {'Status':<12} {'Multi-AZ':<9} {'Enc':<4} {'Public'}")
                print(f"  {'─'*28} {'─'*15} {'─'*15} {'─'*12} {'─'*9} {'─'*4} {'─'*6}")
                for db in instances:
                    maz = "✓" if db.multi_az else "✗"
                    enc = "✓" if db.encrypted else "✗"
                    pub = "✓" if db.publicly_accessible else "✗"
                    print(f"  {db.db_id[:28]:<28} {db.engine:<15} {db.instance_class:<15} {db.status:<12} {maz:<9} {enc:<4} {pub}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _list_dynamodb(self) -> None:
        provider_name = self.session.provider or "aws"
        gate = ensure_provider_configured(provider_name)
        if not gate.success:
            self.print_error(gate.error)
            input("Press Enter to continue...")
            return

        region_result = ensure_region_configured(self.session)
        if not region_result.success:
            self.print_error(region_result.message or "Region required.")
            input("Press Enter to continue...")
            return
        s = get_session()

        print("\nFetching DynamoDB tables...")
        try:
            provider = get_database_provider(provider_name)
            tables = provider.list_nosql_tables(
                region=s.region,
                profile=s.profile,
            )
            if not tables:
                print("\nNo DynamoDB tables found.")
            else:
                print(f"\nFound {len(tables)} table(s):\n")
                print(f"  {'Table Name':<35} {'Status':<12} {'Items':<10} {'Billing':<16} {'RCU':<6} {'WCU'}")
                print(f"  {'─'*35} {'─'*12} {'─'*10} {'─'*16} {'─'*6} {'─'*6}")
                for t in tables:
                    print(f"  {t.table_name[:35]:<35} {t.status:<12} {t.item_count:<10} {t.billing_mode:<16} {t.read_capacity:<6} {t.write_capacity}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _find_public_dbs(self) -> None:
        provider_name = self.session.provider or "aws"
        gate = ensure_provider_configured(provider_name)
        if not gate.success:
            self.print_error(gate.error)
            input("Press Enter to continue...")
            return

        region_result = ensure_region_configured(self.session)
        if not region_result.success:
            self.print_error(region_result.message or "Region required.")
            input("Press Enter to continue...")
            return
        s = get_session()

        print("\nChecking for publicly accessible databases...")
        try:
            provider = get_database_provider(provider_name)
            instances = provider.list_db_instances(
                region=s.region,
                profile=s.profile,
            )
            public = provider.find_publicly_accessible(instances)
            if not public:
                print("\n✓ No publicly accessible databases found. Good security posture!")
            else:
                print(f"\n⚠ Found {len(public)} publicly accessible database(s):\n")
                print(f"  {'DB ID':<28} {'Engine':<15} {'Endpoint'}")
                print(f"  {'─'*28} {'─'*15} {'─'*40}")
                for db in public:
                    print(f"  {db.db_id[:28]:<28} {db.engine:<15} {db.endpoint}")
                print(f"\n  Recommendation: Disable public access unless explicitly required.")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")
