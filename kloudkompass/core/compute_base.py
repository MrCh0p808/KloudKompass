# kloudkompass/core/compute_base.py
# --------------------------------
# Abstract base for compute resource management. All cloud-specific
# compute modules (EC2, Azure VMs, GCE) inherit from this and implement
# these methods. The normalized output format ensures the CLI and TUI
# can display compute resources from any provider the same way.

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from kloudkompass.core.provider_base import ProviderBase


@dataclass
class ComputeInstance:
    """
    Normalized compute instance record.

    This dataclass ensures that EC2 instances, Azure VMs, and GCE instances
    all look the same to the CLI and TUI. Each provider's compute module
    transforms their native response into this format.
    """
    instance_id: str       # Provider-specific ID (i-0abc123, /subscriptions/...)
    name: str              # Name tag or identifier
    instance_type: str     # Machine type (t3.micro, Standard_B1s, e2-micro)
    state: str             # running, stopped, terminated, etc.
    region: str            # Region or zone
    public_ip: str = ""    # Public IP if assigned
    private_ip: str = ""   # Private IP
    launch_time: str = ""  # ISO timestamp of launch/creation
    platform: str = ""     # Linux, Windows, etc.
    vpc_id: str = ""       # VPC/VNet ID
    tags: Dict[str, str] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "instance_id": self.instance_id,
            "name": self.name,
            "instance_type": self.instance_type,
            "state": self.state,
            "region": self.region,
            "public_ip": self.public_ip,
            "private_ip": self.private_ip,
            "launch_time": self.launch_time,
            "platform": self.platform,
            "vpc_id": self.vpc_id,
            "tags": self.tags,
        }


class ComputeProvider(ProviderBase):
    """
    Abstract base for compute resource operations.

    Each cloud provider implements these methods to list, describe,
    and manage compute instances. Return type is always List[ComputeInstance]
    so the CLI and TUI can handle all providers uniformly.
    """

    @abstractmethod
    def list_instances(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[ComputeInstance]:
        """
        List all compute instances.

        Args:
            region: Cloud region to query. None means default/all.
            profile: CLI profile to use. None means default.
            filters: Key-value filters (e.g., {"state": "running"}).

        Returns:
            List of ComputeInstance records sorted by name.
        """
        pass

    @abstractmethod
    def get_instance(
        self,
        instance_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> Optional[ComputeInstance]:
        """
        Get details for a single instance by ID.

        Returns None if the instance is not found.
        """
        pass

    @abstractmethod
    def start_instance(
        self,
        instance_ids: List[str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """
        Start stopped instances.

        Returns True if the start command was accepted.
        """
        pass

    @abstractmethod
    def stop_instance(
        self,
        instance_ids: List[str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """
        Stop running instances.

        Returns True if the stop command was accepted.
        """
        pass

    @abstractmethod
    def reboot_instance(
        self,
        instance_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """
        Reboot a running instance.

        Returns True if the reboot command was accepted.
        """
        pass

    @abstractmethod
    def add_tags(
        self,
        resource_ids: List[str],
        tags: Dict[str, str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Add or update tags on specified resources."""
        pass

    @abstractmethod
    def remove_tags(
        self,
        resource_ids: List[str],
        tag_keys: List[str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Remove tags from specified resources."""
        pass

    def filter_by_state(
        self,
        instances: List[ComputeInstance],
        state: str,
    ) -> List[ComputeInstance]:
        """Filter instances by state (running, stopped, terminated)."""
        return [i for i in instances if i.state.lower() == state.lower()]

    def filter_by_tag(
        self,
        instances: List[ComputeInstance],
        tag_key: str,
        tag_value: Optional[str] = None,
    ) -> List[ComputeInstance]:
        """
        Filter instances by tag.

        If tag_value is None, matches any instance with that tag key.
        If tag_value is provided, matches exact key=value.
        """
        results = []
        for inst in instances:
            if tag_key in inst.tags:
                if tag_value is None or inst.tags[tag_key] == tag_value:
                    results.append(inst)
        return results
