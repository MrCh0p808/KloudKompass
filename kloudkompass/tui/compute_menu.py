# kloudkompass/tui/compute_menu.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Compute (EC2) resource viewer screen.
# Phase 3: Uses provider factory and get_input() navigation.

from typing import Optional

from kloudkompass.tui.screens import Screen
from kloudkompass.tui.session import update_session, get_session
from kloudkompass.tui.provider_setup import ensure_provider_configured
from kloudkompass.tui.prompts import ensure_region_configured
from kloudkompass.core.provider_factory import get_compute_provider
from kloudkompass.core.exceptions import KloudKompassError


COMPUTE_OPTIONS = [
    ("1", "List all instances"),
    ("2", "List running instances"),
    ("3", "List stopped instances"),
    ("4", "View instance details"),
    ("5", "Filter instances by Tag"),
    ("6", "Filter by Instance Type"),
    ("7", "Filter by Availability Zone"),
    ("8", "Manage Instance Tags"),
]


class ComputeMenuScreen(Screen):
    """
    Compute resources viewer.

    Lists EC2 instances with state filtering and detail drill-down.
    """

    title = "Compute Resources (EC2)"

    def render(self) -> None:
        provider = self.session.provider or "aws"
        print(f"  Provider: {provider.upper()}")
        print()
        for key, label in COMPUTE_OPTIONS:
            print(f"  {key}. {label}")
        self.print_nav_hint()

    def handle_input(self) -> Optional[Screen]:
        # Ensure provider is set
        if not self.session.provider:
            update_session(self.session.with_provider("aws"))

        result = self.get_input()

        if result.is_quit:
            return "exit"
        if result.is_back:
            return "back"

        choice = result.raw

        if choice == "1":
            self._list_instances()
        elif choice == "2":
            self._list_instances(state_filter="running")
        elif choice == "3":
            self._list_instances(state_filter="stopped")
        elif choice == "4":
            self._view_instance_details()
        elif choice == "5":
            self._filter_by_tag()
        elif choice == "6":
            self._filter_by_type()
        elif choice == "7":
            self._filter_by_az()
        elif choice == "8":
            self._manage_tags()
        else:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")

        return None

    def _filter_by_tag(self) -> None:
        """Prompt for a tag and list matching instances."""
        result = self.get_input("Enter Tag (Format: Key=Value or skip for any): ")
        if result.is_quit or result.is_back:
            return
            
        tag_str = result.raw.strip()
        if not tag_str:
            print("\nNo tag provided.")
            input("Press Enter to continue...")
            return
            
        tags_dict = {}
        if "=" in tag_str:
            k, v = tag_str.split("=", 1)
            tags_dict[k] = v
        else:
            tags_dict[tag_str] = ""
            
        self._list_instances(tags=tags_dict)

    def _filter_by_type(self) -> None:
        """Prompt for instance type and list matching instances."""
        result = self.get_input("Enter Instance Type (e.g. t2.micro, m5.large): ")
        if result.is_quit or result.is_back:
            return
            
        itype = result.raw.strip()
        if not itype:
            print("\nNo type provided.")
            input("Press Enter to continue...")
            return
            
        self._list_instances(custom_filters={"instance-type": itype})

    def _filter_by_az(self) -> None:
        """Prompt for Availability Zone and list matching instances."""
        result = self.get_input("Enter Availability Zone (e.g. us-east-1a): ")
        if result.is_quit or result.is_back:
            return
            
        az = result.raw.strip()
        if not az:
            print("\nNo AZ provided.")
            input("Press Enter to continue...")
            return
            
        self._list_instances(custom_filters={"availability-zone": az})

    def _manage_tags(self) -> None:
        """Add or remove tags from an instance."""
        provider_name = self.session.provider or "aws"
        gate_result = ensure_provider_configured(provider_name)
        if not gate_result.success:
            self.print_error(gate_result.error)
            input("Press Enter to continue...")
            return
            
        region_result = ensure_region_configured(self.session)
        if not region_result.success:
            self.print_error(region_result.message or "Region required.")
            input("Press Enter to continue...")
            return
        current_session = get_session()
        
        provider = get_compute_provider(provider_name)

        result = self.get_input("\nEnter Instance ID to manage tags for: ")
        if result.is_quit or result.is_back:
            return
        instance_id = result.raw.strip()
        if not instance_id:
            return

        print("\n  1. Add/Update Tag\n  2. Remove Tag")
        action_res = self.get_input("Action: ")
        if action_res.is_quit or action_res.is_back:
            return
            
        action = action_res.raw.strip()
        if action not in ("1", "2"):
            print("\nInvalid action.")
            input("Press Enter to continue...")
            return
            
        if action == "1":
            tag_res = self.get_input("Enter Tag to Add/Update (Key=Value): ")
            if tag_res.is_quit or tag_res.is_back or not tag_res.raw.strip():
                return
            tag_str = tag_res.raw.strip()
            if "=" not in tag_str:
                print("\nInvalid format. Must be Key=Value.")
                input("Press Enter to continue...")
                return
            k, v = tag_str.split("=", 1)
            print(f"\nAdding tag '{k}={v}' to {instance_id}...")
            success = provider.add_tags([instance_id], {k: v}, region=current_session.region, profile=current_session.profile)
            if success:
                print("\n✓ Tag added successfully.")
            else:
                print("\n✗ Failed to add tag.")
        else:
            tag_res = self.get_input("Enter Tag Key to Remove (e.g. Environment): ")
            if tag_res.is_quit or tag_res.is_back or not tag_res.raw.strip():
                return
            k = tag_res.raw.strip()
            print(f"\nRemoving tag '{k}' from {instance_id}...")
            success = provider.remove_tags([instance_id], [k], region=current_session.region, profile=current_session.profile)
            if success:
                print("\n✓ Tag removed successfully.")
            else:
                print("\n✗ Failed to remove tag.")
                
        input("Press Enter to continue...")

    def _list_instances(self, state_filter: str = None, tags: dict = None, custom_filters: dict = None) -> None:
        """List EC2 instances with optional state, tag, or custom filtering."""
        provider_name = self.session.provider or "aws"

        gate_result = ensure_provider_configured(provider_name)
        if not gate_result.success:
            self.print_error(gate_result.error)
            input("Press Enter to continue...")
            return

        # Region gate — ensures region is set before AWS calls
        region_result = ensure_region_configured(self.session)
        if not region_result.success:
            self.print_error(region_result.message or "Region required.")
            input("Press Enter to continue...")
            return
        # Refresh session after potential region update
        current_session = get_session()

        print(f"\nFetching instances{f' (state: {state_filter})' if state_filter else ''}...")

        try:
            provider = get_compute_provider(provider_name)
            filters = {}
            if state_filter:
                filters["instance-state-name"] = state_filter
            if custom_filters:
                filters.update(custom_filters)
                
            if not filters:
                filters = None

            instances = provider.list_instances(
                region=current_session.region,
                profile=current_session.profile,
                filters=filters,
                tags=tags,
            )

            if not instances:
                print("\nNo instances found matching criteria.")
                input("Press Enter to continue...")
            else:
                print(f"\nFound {len(instances)} instance(s):\n")
                # Header with row numbers
                print(f"  {'#':<4} {'ID':<20} {'Name':<25} {'Type':<14} {'State':<12} {'Public IP':<16}")
                print(f"  {'─'*4} {'─'*20} {'─'*25} {'─'*14} {'─'*12} {'─'*16}")
                for idx, inst in enumerate(instances, 1):
                    state_color = inst.state
                    print(f"  {idx:<4} {inst.instance_id:<20} {inst.name[:25]:<25} {inst.instance_type:<14} {state_color:<12} {inst.public_ip or '—':<16}")

                # Drill-down / Batch selection
                print()
                sel = self.get_input("Enter # to view details, or comma-separated list (e.g. 1,2,3) for batch operations (or Enter to go back): ")
                if sel.is_quit:
                    return
                if sel.is_back or not sel.raw.strip():
                    return
                
                raw_input = sel.raw.strip()
                
                # Try parsing as batch selections
                try:
                    indices = self._parse_indices(raw_input, len(instances))
                    if not indices:
                        print("\nInvalid selection.")
                        input("Press Enter to continue...")
                        return
                    
                    if len(indices) == 1:
                        # Single selection, default to detail view
                        self._show_instance_detail(instances[indices[0]])
                    else:
                        # Multiple selected, open batch processing menu
                        selected_instances = [instances[i] for i in indices]
                        self._handle_batch_actions(provider, current_session, selected_instances)
                        
                except ValueError as e:
                    print(f"\n{e}")
                    input("Press Enter to continue...")

        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _parse_indices(self, raw_input: str, max_len: int) -> list[int]:
        """Parse comma-separated or range inputs into a valid integer index list."""
        indices = set()
        parts = raw_input.split(',')
        for part in parts:
            part = part.strip()
            if not part: continue
            
            if '-' in part:
                start_str, end_str = part.split('-', 1)
                start_idx = int(start_str) - 1
                end_idx = int(end_str) - 1
                if start_idx > end_idx or start_idx < 0 or end_idx >= max_len:
                    raise ValueError(f"Invalid range: {part}")
                indices.update(range(start_idx, end_idx + 1))
            else:
                idx = int(part) - 1
                if idx < 0 or idx >= max_len:
                    raise ValueError(f"Invalid index: {part}")
                indices.add(idx)
        return sorted(list(indices))

    def _handle_batch_actions(self, provider, session, instances: list) -> None:
        """Handle batch modifications to multiple EC2 instances."""
        instance_ids = [i.instance_id for i in instances]
        
        while True:
            print(f"\n  Batch Operations ({len(instances)} instances selected):")
            print("  1. Start Instances")
            print("  2. Stop Instances")
            print("  3. Add/Update Tag")
            print("  4. Remove Tag")
            print("  5. Go Back")
            
            res = self.get_input("\nAction: ")
            if res.is_quit or res.is_back or res.raw.strip() == "5":
                return
                
            action = res.raw.strip()
            
            if action == "1":
                print(f"\nStarting {len(instances)} instances...")
                if provider.start_instance(instance_ids, region=session.region, profile=session.profile):
                    print("\n✓ Command accepted successfully.")
                else:
                    print("\n✗ Command failed.")
                input("Press Enter to continue...")
                return
                
            elif action == "2":
                print(f"\nStopping {len(instances)} instances...")
                if provider.stop_instance(instance_ids, region=session.region, profile=session.profile):
                    print("\n✓ Command accepted successfully.")
                else:
                    print("\n✗ Command failed.")
                input("Press Enter to continue...")
                return
                
            elif action == "3":
                tag_res = self.get_input("Enter Tag to Add/Update (Key=Value): ")
                if tag_res.is_quit or tag_res.is_back or not tag_res.raw.strip():
                    continue
                tag_str = tag_res.raw.strip()
                if "=" not in tag_str:
                    print("\nInvalid format. Must be Key=Value.")
                    input("Press Enter to continue...")
                    continue
                k, v = tag_str.split("=", 1)
                print(f"\nAdding tag '{k}={v}' to {len(instances)} instances...")
                if provider.add_tags(instance_ids, {k: v}, region=session.region, profile=session.profile):
                    print("\n✓ Tags added successfully.")
                else:
                    print("\n✗ Failed to add tags.")
                input("Press Enter to continue...")
                return
                
            elif action == "4":
                tag_res = self.get_input("Enter Tag Key to Remove (e.g. Environment): ")
                if tag_res.is_quit or tag_res.is_back or not tag_res.raw.strip():
                    continue
                k = tag_res.raw.strip()
                print(f"\nRemoving tag '{k}' from {len(instances)} instances...")
                if provider.remove_tags(instance_ids, [k], region=session.region, profile=session.profile):
                    print("\n✓ Tags removed successfully.")
                else:
                    print("\n✗ Failed to remove tags.")
                input("Press Enter to continue...")
                return
                
            else:
                print("\nInvalid action.")
                input("Press Enter to continue...")

    def _show_instance_detail(self, instance) -> None:
        """Display detailed info for a single instance (drill-down)."""
        print(f"\n  Instance Details:")
        print(f"  {'─'*40}")
        print(f"  ID:           {instance.instance_id}")
        print(f"  Name:         {instance.name}")
        print(f"  Type:         {instance.instance_type}")
        print(f"  State:        {instance.state}")
        print(f"  Region/AZ:    {instance.region}")
        print(f"  Public IP:    {instance.public_ip or '—'}")
        print(f"  Private IP:   {instance.private_ip or '—'}")
        print(f"  VPC:          {instance.vpc_id or '—'}")
        print(f"  Platform:     {instance.platform}")
        print(f"  Launch Time:  {instance.launch_time}")
        if instance.tags:
            print(f"  Tags:")
            for k, v in instance.tags.items():
                print(f"    {k}: {v}")
        print()
        input("Press Enter to continue...")

    def _view_instance_details(self) -> None:
        """View details for a specific instance by ID."""
        provider_name = self.session.provider or "aws"

        gate_result = ensure_provider_configured(provider_name)
        if not gate_result.success:
            self.print_error(gate_result.error)
            input("Press Enter to continue...")
            return

        # Region gate
        region_result = ensure_region_configured(self.session)
        if not region_result.success:
            self.print_error(region_result.message or "Region required.")
            input("Press Enter to continue...")
            return
        current_session = get_session()

        result = self.get_input("Enter Instance ID: ")
        if result.is_quit or result.is_back:
            return

        instance_id = result.raw.strip()
        if not instance_id:
            print("\nNo instance ID provided.")
            input("Press Enter to continue...")
            return

        print(f"\nFetching details for {instance_id}...")

        try:
            provider = get_compute_provider(provider_name)
            instance = provider.get_instance(
                instance_id=instance_id,
                region=current_session.region,
                profile=current_session.profile,
            )

            if not instance:
                print(f"\nInstance {instance_id} not found.")
                input("Press Enter to continue...")
            else:
                self._show_instance_detail(instance)

        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")
