# kloudkompass/azure/compute.py
# ----------------------------
# Azure Resource Manager (ARM) compute provider implementation.
# Uses the Azure CLI 'vm' commands to list and manage Virtual Machines.
# Normalized to ComputeInstance records for cross-cloud compatibility.

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from kloudkompass.core.compute_base import ComputeProvider, ComputeInstance
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.infra.azure_cli_adapter import get_azure_cli_adapter
from kloudkompass.utils.logger import debug


class AzureComputeProvider(ComputeProvider):
    """
    Azure implementation of the ComputeProvider interface.
    """

    provider_name = "azure"
    cli_command = "az"

    def __init__(self):
        self._adapter = get_azure_cli_adapter()

    def get_manifest(self) -> dict:
        return {
            "compute": {
                "label": "☁️  VMs",
                "tooltip": "Manage Azure Virtual Machines",
                "icon": "☁️",
                "id": "nav_compute"
            }
        }

    def get_custom_actions(self, resource_type: str, resource_id: str) -> List[Dict[str, str]]:
        """
        Azure-specific specialized actions. 
        Explicit toggle between PowerOff (Reserved) and Deallocate (Unbilled).
        """
        if resource_type == "compute":
            return [
                {"name": "Deallocate", "id": "azure_deallocate", "variant": "warning", "tooltip": "Stop AND release hardware (Stops billing)"},
                {"name": "Power Off", "id": "azure_stop", "variant": "error", "tooltip": "Stop but keep hardware reserved (Billing continues)"}
            ]
        return []

    def is_available(self) -> bool:
        return self._adapter.is_available()

    def validate_credentials(self) -> bool:
        is_valid, _ = self._adapter.check_credentials()
        return is_valid

    def _parse_vm(self, vm_data: Dict[str, Any]) -> ComputeInstance:
        """Map Azure VM data to normalized ComputeInstance."""
        power_state = "unknown"
        # Azure list -d returns PowerState/running, PowerState/deallocated, etc.
        ps = vm_data.get("powerState", "")
        if "running" in ps: power_state = "running"
        elif "deallocated" in ps: power_state = "deallocated"
        elif "stopped" in ps: power_state = "stopped"
        elif "starting" in ps: power_state = "starting"
        
        tags = vm_data.get("tags", {})
        
        return ComputeInstance(
            instance_id=vm_data.get("id", ""),
            name=vm_data.get("name", ""),
            instance_type=vm_data.get("hardwareProfile", {}).get("vmSize", ""),
            state=power_state,
            region=vm_data.get("location", ""),
            public_ip=vm_data.get("publicIps", ""),
            private_ip=vm_data.get("privateIps", ""),
            launch_time="", # Azure uses different APIs for creation time
            platform=vm_data.get("storageProfile", {}).get("osDisk", {}).get("osType", "Linux"),
            vpc_id="", 
            tags=tags,
            raw_data=vm_data
        )

    def list_instances(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[ComputeInstance]:
        """
        List Azure VMs using az vm list -d for status enrichment.
        """
        sub = self._adapter.get_active_subscription(profile)
        # Use -d for 'show-details' which includes powerState
        cmd = ["vm", "list", "-d", "--subscription", sub]
        
        data = self._adapter.run_cmd_json(cmd)
        instances = [self._parse_vm(vm) for vm in data]
        
        # Sort by name
        instances.sort(key=lambda i: i.name.lower())
        return instances

    def get_instance(
        self,
        instance_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> Optional[ComputeInstance]:
        sub = self._adapter.get_active_subscription(profile)
        # instance_id is fully qualified in Azure (/subscriptions/...)
        cmd = ["vm", "show", "-d", "--ids", instance_id]
        data = self._adapter.run_cmd_json(cmd)
        if data:
            return self._parse_vm(data)
        return None

    def start_instance(self, instance_ids: List[str], region: Optional[str] = None, profile: Optional[str] = None) -> bool:
        sub = self._adapter.get_active_subscription(profile)
        cmd = ["vm", "start", "--ids"] + instance_ids
        return self._adapter.run_cmd(cmd)

    def stop_instance(self, instance_ids: List[str], region: Optional[str] = None, profile: Optional[str] = None) -> bool:
        """Default Azure stop maps to 'deallocate' to save user money."""
        return self.deallocate_instance(instance_ids, profile)

    def deallocate_instance(self, instance_ids: List[str], profile: Optional[str] = None) -> bool:
        """Stop VM and release hardware (Billing stops)."""
        sub = self._adapter.get_active_subscription(profile)
        cmd = ["vm", "deallocate", "--ids"] + instance_ids
        return self._adapter.run_cmd(cmd)

    def power_off_instance(self, instance_ids: List[str], profile: Optional[str] = None) -> bool:
        """Power off but keep reservation (Billing continues)."""
        sub = self._adapter.get_active_subscription(profile)
        cmd = ["vm", "stop", "--ids"] + instance_ids
        return self._adapter.run_cmd(cmd)

    def reboot_instance(self, instance_id: str, region: Optional[str] = None, profile: Optional[str] = None) -> bool:
        sub = self._adapter.get_active_subscription(profile)
        cmd = ["vm", "restart", "--ids", instance_id]
        return self._adapter.run_cmd(cmd)

    def add_tags(self, resource_ids: List[str], tags: Dict[str, str], region: Optional[str] = None, profile: Optional[str] = None) -> bool:
        # Azure uses az resource tag or az vm update --set tags
        # Implement simplified resource tagging via adapter rest/resourcetag
        return False # Stub for now

    def remove_tags(self, resource_ids: List[str], tag_keys: List[str], region: Optional[str] = None, profile: Optional[str] = None) -> bool:
        return False # Stub for now
