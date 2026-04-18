# kloudkompass/tui/storage_menu.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Storage (S3/EBS) viewer screen.

from typing import Optional

from kloudkompass.tui.screens import Screen
from kloudkompass.tui.session import update_session, get_session
from kloudkompass.tui.provider_setup import ensure_provider_configured
from kloudkompass.tui.prompts import ensure_region_configured
from kloudkompass.core.provider_factory import get_storage_provider
from kloudkompass.core.exceptions import KloudKompassError


STORAGE_OPTIONS = [
    ("1", "List S3 Buckets"),
    ("2", "List EBS Volumes"),
    ("3", "Find Unattached Volumes"),
    ("4", "Filter resources by Tag"),
    ("5", "Filter S3 by Region"),
    ("6", "Filter S3 by Public Access"),
]


class StorageMenuScreen(Screen):
    """Storage resources viewer — S3 buckets and EBS volumes."""

    title = "Storage Resources (S3/EBS)"

    def render(self) -> None:
        provider = self.session.provider or "aws"
        print(f"  Provider: {provider.upper()}")
        print()
        for key, label in STORAGE_OPTIONS:
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
            self._list_buckets()
        elif choice == "2":
            self._list_volumes()
        elif choice == "3":
            self._find_unattached()
        elif choice == "4":
            self._filter_by_tag()
        elif choice == "5":
            self._filter_s3_by_region()
        elif choice == "6":
            self._filter_s3_by_public()
        else:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")
        return None

    def _filter_by_tag(self) -> None:
        print("\n  1. S3 Buckets\n  2. EBS Volumes")
        res = self.get_input("Select resource to filter: ")
        if res.is_quit or res.is_back or res.raw not in ("1", "2"):
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
            self._list_buckets(tags=tags_dict)
        elif r_type == "2":
            self._list_volumes(tags=tags_dict)

    def _filter_s3_by_region(self) -> None:
        """Prompt for region and list matching buckets."""
        res = self.get_input("Enter Region (e.g. us-east-1): ")
        if res.is_quit or res.is_back or not res.raw.strip():
            return
        self._list_buckets(filters={"region": res.raw.strip()})

    def _filter_s3_by_public(self) -> None:
        """Prompt for access level and list matching buckets."""
        res = self.get_input("Enter Access Level (public/private): ")
        if res.is_quit or res.is_back or not res.raw.strip():
            return
        level = res.raw.strip().lower()
        if level not in ("public", "private"):
            print("\nInvalid. Must be 'public' or 'private'.")
            input("Press Enter to continue...")
            return
        self._list_buckets(filters={"public-access": level})

    def _list_buckets(self, tags: dict = None, filters: dict = None) -> None:
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

        print("\nFetching S3 buckets...")
        try:
            provider = get_storage_provider(provider_name)
            buckets = provider.list_buckets(profile=s.profile, tags=tags, filters=filters)
            if not buckets:
                print("\nNo S3 buckets found.")
            else:
                print(f"\nFound {len(buckets)} bucket(s):\n")
                print(f"  {'Bucket Name':<45} {'Region':<15} {'Access':<10} {'Created'}")
                print(f"  {'─'*45} {'─'*15} {'─'*10} {'─'*25}")
                for b in buckets:
                    print(f"  {b.bucket_name:<45} {b.region:<15} {b.access_level:<10} {b.creation_date[:19] if b.creation_date else '—'}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _list_volumes(self, tags: dict = None) -> None:
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

        print("\nFetching EBS volumes...")
        try:
            provider = get_storage_provider(provider_name)
            volumes = provider.list_volumes(
                region=s.region,
                profile=s.profile,
                tags=tags,
            )
            if not volumes:
                print("\nNo EBS volumes found.")
                input("Press Enter to continue...")
            else:
                print(f"\nFound {len(volumes)} volume(s):\n")
                print(f"  {'#':<4} {'Volume ID':<24} {'Name':<20} {'Size':<8} {'Type':<8} {'State':<12} {'Attached To':<20} {'Enc'}")
                print(f"  {'─'*4} {'─'*24} {'─'*20} {'─'*8} {'─'*8} {'─'*12} {'─'*20} {'─'*3}")
                for idx, v in enumerate(volumes, 1):
                    enc = "✓" if v.encrypted else "✗"
                    print(f"  {idx:<4} {v.volume_id:<24} {v.name[:20]:<20} {v.size_gb:<8} {v.volume_type:<8} {v.state:<12} {v.attached_to or '—':<20} {enc}")

                # Drill-down: show volume details
                print()
                sel = self.get_input("Enter # to view details (or Enter to go back): ")
                if sel.is_quit or sel.is_back or not sel.raw.strip():
                    return
                try:
                    idx = int(sel.raw.strip()) - 1
                    if 0 <= idx < len(volumes):
                        self._show_volume_detail(volumes[idx])
                    else:
                        print("\nInvalid selection.")
                        input("Press Enter to continue...")
                except ValueError:
                    print("\nInvalid number.")
                    input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")

    def _show_volume_detail(self, v) -> None:
        """Drill-down: display detailed volume information."""
        enc = "✓ Encrypted" if v.encrypted else "✗ Not encrypted"
        print(f"\n  Volume Details:")
        print(f"  {'─'*40}")
        print(f"  Volume ID:    {v.volume_id}")
        print(f"  Name:         {v.name or '—'}")
        print(f"  Size:         {v.size_gb} GB")
        print(f"  Type:         {v.volume_type}")
        print(f"  State:        {v.state}")
        print(f"  Attached To:  {v.attached_to or '— (unattached)'}")
        print(f"  Region:       {v.region}")
        print(f"  Encryption:   {enc}")
        if v.tags:
            print(f"  Tags:")
            for k, val in v.tags.items():
                print(f"    {k}: {val}")
        print()
        input("Press Enter to continue...")

    def _find_unattached(self) -> None:
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

        print("\nFinding unattached EBS volumes (potential waste)...")
        try:
            provider = get_storage_provider(provider_name)
            volumes = provider.list_volumes(
                region=s.region,
                profile=s.profile,
            )
            unattached = provider.find_unattached_volumes(volumes)
            if not unattached:
                print("\n✓ No unattached volumes found. No waste detected.")
            else:
                total_gb = sum(v.size_gb for v in unattached)
                print(f"\n⚠ Found {len(unattached)} unattached volume(s) ({total_gb} GB total):\n")
                print(f"  {'Volume ID':<24} {'Name':<20} {'Size (GB)':<10} {'Type':<8} {'Region'}")
                print(f"  {'─'*24} {'─'*20} {'─'*10} {'─'*8} {'─'*16}")
                for v in unattached:
                    print(f"  {v.volume_id:<24} {v.name[:20]:<20} {v.size_gb:<10} {v.volume_type:<8} {v.region}")
            print()
            input("Press Enter to continue...")
        except KloudKompassError as e:
            self.print_error(str(e))
            input("Press Enter to continue...")
