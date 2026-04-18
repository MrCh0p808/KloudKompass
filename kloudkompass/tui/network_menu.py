# kloudkompass/tui/network_menu.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Networking (VPC/SG/Subnet) viewer screen.

from typing import Optional

from kloudkompass.tui.screens import Screen
from kloudkompass.tui.session import update_session, get_session
from kloudkompass.tui.provider_setup import ensure_provider_configured
from kloudkompass.tui.prompts import ensure_region_configured
from kloudkompass.core.provider_factory import get_network_provider
from kloudkompass.core.exceptions import KloudKompassError


NETWORK_OPTIONS = [
    ("1", "List VPCs"),
    ("2", "List Subnets"),
    ("3", "List Security Groups"),
    ("4", "View Security Group Rules"),
    ("5", "Filter resources by Tag"),
]


class NetworkMenuScreen(Screen):
    """Networking resources viewer — VPCs, Subnets, Security Groups."""

    title = "Networking Resources (VPC)"

    def render(self) -> None:
        provider = self.session.provider or "aws"
        print(f"  Provider: {provider.upper()}")
        print()
        for key, label in NETWORK_OPTIONS:
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
            self._list_vpcs()
        elif choice == "2":
            self._list_subnets()
        elif choice == "3":
            self._list_security_groups()
        elif choice == "4":
            self._view_sg_rules()
        elif choice == "5":
            self._filter_by_tag()
        else:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")
        return None

    def _filter_by_tag(self) -> None:
        print("\n  1. VPCs\n  2. Subnets\n  3. Security Groups")
        res = self.get_input("Select resource to filter: ")
        if res.is_quit or res.is_back or res.raw not in ("1", "2", "3"):
            return
            
        r_type = res.raw
        tag_res = self.get_input("Enter Tag (Key=Value): ")
        if tag_res.is_quit or tag_res.is_back or not tag_res.raw.strip():
            return
            
        tag_str = tag_res.raw.strip()
        tags_dict = {}
        if "=" in tag_str:
            k, v = tag_str.split("=", 1)
            tags_dict[k] = v
        else:
            tags_dict[tag_str] = ""
            
        if r_type == "1":
            self._list_vpcs(tags=tags_dict)
        elif r_type == "2":
            self._list_subnets(tags=tags_dict)
        elif r_type == "3":
            self._list_security_groups(tags=tags_dict)

    def _list_vpcs(self, tags: dict = None) -> None:
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

        print("\nFetching VPCs...")
        try:
            provider = get_network_provider(provider_name)
            vpcs = provider.list_vpcs(
                region=s.region,
                profile=s.profile,
                tags=tags,
            )
            if not vpcs:
                print("\nNo VPCs found.")
                input("Press Enter to continue...")
            else:
                print(f"\nFound {len(vpcs)} VPC(s):\n")
                print(f"  {'#':<4} {'VPC ID':<24} {'Name':<25} {'CIDR':<18} {'State':<12} {'Default'}")
                print(f"  {'─'*4} {'─'*24} {'─'*25} {'─'*18} {'─'*12} {'─'*7}")
                for idx, vpc in enumerate(vpcs, 1):
                    default = "✓" if vpc.is_default else ""
                    print(f"  {idx:<4} {vpc.vpc_id:<24} {vpc.name[:25]:<25} {vpc.cidr_block:<18} {vpc.state:<12} {default}")

                # Drill-down: show subnets in selected VPC
                print()
                sel = self.get_input("Enter # to view subnets in VPC (or Enter to go back): ")
                if sel.is_quit or sel.is_back or not sel.raw.strip():
                    return
                try:
                    idx = int(sel.raw.strip()) - 1
                    if 0 <= idx < len(vpcs):
                        self._list_subnets_for_vpc(vpcs[idx], provider_name, s)
                    else:
                        print("\nInvalid selection.")
                        input("Press Enter to continue...")
                except ValueError:
                    print("\nInvalid number.")
                    input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _list_subnets(self, tags: dict = None) -> None:
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

        print("\nFetching subnets...")
        try:
            provider = get_network_provider(provider_name)
            subnets = provider.list_subnets(
                region=s.region,
                profile=s.profile,
                tags=tags,
            )
            if not subnets:
                print("\nNo subnets found.")
            else:
                print(f"\nFound {len(subnets)} subnet(s):\n")
                print(f"  {'Subnet ID':<26} {'Name':<20} {'CIDR':<18} {'AZ':<16} {'IPs':<6} {'Public'}")
                print(f"  {'─'*26} {'─'*20} {'─'*18} {'─'*16} {'─'*6} {'─'*6}")
                for subnet in subnets:
                    pub = "✓" if subnet.is_public else ""
                    print(f"  {subnet.subnet_id:<26} {subnet.name[:20]:<20} {subnet.cidr_block:<18} {subnet.availability_zone:<16} {subnet.available_ips:<6} {pub}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _list_security_groups(self, tags: dict = None) -> None:
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

        print("\nFetching security groups...")
        try:
            provider = get_network_provider(provider_name)
            groups = provider.list_security_groups(
                region=s.region,
                profile=s.profile,
                tags=tags,
            )
            if not groups:
                print("\nNo security groups found.")
                input("Press Enter to continue...")
            else:
                print(f"\nFound {len(groups)} security group(s):\n")
                print(f"  {'#':<4} {'Group ID':<22} {'Name':<25} {'VPC':<24} {'In':<5} {'Out'}")
                print(f"  {'─'*4} {'─'*22} {'─'*25} {'─'*24} {'─'*5} {'─'*5}")
                for idx, sg in enumerate(groups, 1):
                    print(f"  {idx:<4} {sg.group_id:<22} {sg.name[:25]:<25} {sg.vpc_id:<24} {len(sg.inbound_rules):<5} {len(sg.outbound_rules)}")

                # Drill-down: show rules for selected SG
                print()
                sel = self.get_input("Enter # to view rules (or Enter to go back): ")
                if sel.is_quit or sel.is_back or not sel.raw.strip():
                    return
                try:
                    idx = int(sel.raw.strip()) - 1
                    if 0 <= idx < len(groups):
                        self._show_sg_detail(groups[idx])
                    else:
                        print("\nInvalid selection.")
                        input("Press Enter to continue...")
                except ValueError:
                    print("\nInvalid number.")
                    input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _list_subnets_for_vpc(self, vpc, provider_name: str, s) -> None:
        """Drill-down: list subnets belonging to a specific VPC."""
        print(f"\n  Subnets in VPC: {vpc.name} ({vpc.vpc_id})")
        print(f"  {'─'*60}")
        try:
            provider = get_network_provider(provider_name)
            subnets = provider.list_subnets(
                region=s.region,
                profile=s.profile,
            )
            # Filter to this VPC
            vpc_subnets = [sub for sub in subnets if sub.vpc_id == vpc.vpc_id]
            if not vpc_subnets:
                print("  No subnets in this VPC.")
            else:
                print(f"  {len(vpc_subnets)} subnet(s):\n")
                print(f"  {'#':<4} {'Subnet ID':<26} {'Name':<20} {'CIDR':<18} {'AZ':<16} {'IPs':<6} {'Pub'}")
                print(f"  {'─'*4} {'─'*26} {'─'*20} {'─'*18} {'─'*16} {'─'*6} {'─'*3}")
                for idx, sub in enumerate(vpc_subnets, 1):
                    pub = "✓" if sub.is_public else ""
                    print(f"  {idx:<4} {sub.subnet_id:<26} {sub.name[:20]:<20} {sub.cidr_block:<18} {sub.availability_zone:<16} {sub.available_ips:<6} {pub}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _show_sg_detail(self, sg) -> None:
        """Drill-down: show inbound/outbound rules for a security group."""
        print(f"\n  Security Group: {sg.name} ({sg.group_id})")
        print(f"  VPC: {sg.vpc_id}")
        print(f"  Description: {sg.description}")

        print(f"\n  Inbound Rules ({len(sg.inbound_rules)}):")
        if sg.inbound_rules:
            print(f"    {'Protocol':<10} {'Ports':<12} {'CIDR':<20} {'Description'}")
            print(f"    {'─'*10} {'─'*12} {'─'*20} {'─'*20}")
            for rule in sg.inbound_rules:
                proto = rule.get("protocol", "-1")
                from_port = rule.get("from_port", 0)
                to_port = rule.get("to_port", 65535)
                ports = "All" if proto == "-1" else f"{from_port}-{to_port}" if from_port != to_port else str(from_port)
                print(f"    {proto:<10} {ports:<12} {rule.get('cidr', ''):<20} {rule.get('description', '')}")
        else:
            print("    (none)")

        print(f"\n  Outbound Rules ({len(sg.outbound_rules)}):")
        if sg.outbound_rules:
            print(f"    {'Protocol':<10} {'Ports':<12} {'CIDR':<20} {'Description'}")
            print(f"    {'─'*10} {'─'*12} {'─'*20} {'─'*20}")
            for rule in sg.outbound_rules:
                proto = rule.get("protocol", "-1")
                from_port = rule.get("from_port", 0)
                to_port = rule.get("to_port", 65535)
                ports = "All" if proto == "-1" else f"{from_port}-{to_port}" if from_port != to_port else str(from_port)
                print(f"    {proto:<10} {ports:<12} {rule.get('cidr', ''):<20} {rule.get('description', '')}")
        else:
            print("    (none)")

        print()
        input("Press Enter to continue...")

    def _view_sg_rules(self) -> None:
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

        result = self.get_input("Enter Security Group ID: ")
        if result.is_quit or result.is_back:
            return

        sg_id = result.raw.strip()
        if not sg_id:
            print("\nNo Security Group ID provided.")
            input("Press Enter to continue...")
            return

        print(f"\nFetching rules for {sg_id}...")
        try:
            provider = get_network_provider(provider_name)
            sg = provider.get_security_group_rules(
                group_id=sg_id,
                region=s.region,
                profile=s.profile,
            )

            print(f"\n  Security Group: {sg.name} ({sg.group_id})")
            print(f"  VPC: {sg.vpc_id}")
            print(f"  Description: {sg.description}")

            print(f"\n  Inbound Rules ({len(sg.inbound_rules)}):")
            if sg.inbound_rules:
                print(f"    {'Protocol':<10} {'Ports':<12} {'CIDR':<20} {'Description'}")
                print(f"    {'─'*10} {'─'*12} {'─'*20} {'─'*20}")
                for rule in sg.inbound_rules:
                    proto = rule.get("protocol", "-1")
                    from_port = rule.get("from_port", 0)
                    to_port = rule.get("to_port", 65535)
                    ports = "All" if proto == "-1" else f"{from_port}-{to_port}" if from_port != to_port else str(from_port)
                    print(f"    {proto:<10} {ports:<12} {rule.get('cidr', ''):<20} {rule.get('description', '')}")
            else:
                print("    (none)")

            print(f"\n  Outbound Rules ({len(sg.outbound_rules)}):")
            if sg.outbound_rules:
                print(f"    {'Protocol':<10} {'Ports':<12} {'CIDR':<20} {'Description'}")
                print(f"    {'─'*10} {'─'*12} {'─'*20} {'─'*20}")
                for rule in sg.outbound_rules:
                    proto = rule.get("protocol", "-1")
                    from_port = rule.get("from_port", 0)
                    to_port = rule.get("to_port", 65535)
                    ports = "All" if proto == "-1" else f"{from_port}-{to_port}" if from_port != to_port else str(from_port)
                    print(f"    {proto:<10} {ports:<12} {rule.get('cidr', ''):<20} {rule.get('description', '')}")
            else:
                print("    (none)")

            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")
