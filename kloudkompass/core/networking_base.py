# kloudkompass/core/networking_base.py
# ----------------------------------
# Abstract base for networking resource queries. All cloud-specific
# networking modules (AWS VPC, Azure VNet, GCP VPC) inherit from this.
# Normalized output ensures the CLI/TUI can display network resources
# from any provider the same way.

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from kloudkompass.core.provider_base import ProviderBase


@dataclass
class VPCRecord:
    """Normalized VPC/VNet record."""
    vpc_id: str
    name: str
    cidr_block: str
    state: str             # available, pending, etc.
    region: str
    is_default: bool = False
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "vpc_id": self.vpc_id,
            "name": self.name,
            "cidr_block": self.cidr_block,
            "state": self.state,
            "region": self.region,
            "is_default": self.is_default,
            "tags": self.tags,
        }


@dataclass
class SubnetRecord:
    """Normalized subnet record."""
    subnet_id: str
    name: str
    vpc_id: str
    cidr_block: str
    availability_zone: str
    available_ips: int = 0
    is_public: bool = False
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subnet_id": self.subnet_id,
            "name": self.name,
            "vpc_id": self.vpc_id,
            "cidr_block": self.cidr_block,
            "availability_zone": self.availability_zone,
            "available_ips": self.available_ips,
            "is_public": self.is_public,
            "tags": self.tags,
        }


@dataclass
class SecurityGroupRecord:
    """Normalized security group record."""
    group_id: str
    name: str
    description: str
    vpc_id: str
    inbound_rules: List[Dict[str, Any]] = field(default_factory=list)
    outbound_rules: List[Dict[str, Any]] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "group_id": self.group_id,
            "name": self.name,
            "description": self.description,
            "vpc_id": self.vpc_id,
            "inbound_rules": self.inbound_rules,
            "outbound_rules": self.outbound_rules,
            "tags": self.tags,
        }


class NetworkProvider(ProviderBase):
    """
    Abstract base for networking resource queries.

    Each cloud provider implements these methods to list VPCs, subnets,
    and security groups. Return types are always normalized records
    so the CLI and TUI handle all providers uniformly.
    """

    @abstractmethod
    def list_vpcs(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[VPCRecord]:
        """List all VPCs/VNets in the region."""
        pass

    @abstractmethod
    def list_subnets(
        self,
        vpc_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[SubnetRecord]:
        """
        List subnets. If vpc_id is provided, filter to that VPC only.
        """
        pass

    @abstractmethod
    def list_security_groups(
        self,
        vpc_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[SecurityGroupRecord]:
        """
        List security groups/NSGs. If vpc_id provided, filter to that VPC.
        """
        pass

    @abstractmethod
    def get_security_group_rules(
        self,
        group_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> SecurityGroupRecord:
        """Get detailed rules for a specific security group."""
        pass

    def find_open_security_groups(
        self,
        security_groups: List[SecurityGroupRecord],
    ) -> List[SecurityGroupRecord]:
        """
        Find security groups with rules allowing 0.0.0.0/0 inbound.

        This is a security helper — overly permissive rules are a common
        misconfiguration that should be flagged.
        """
        open_groups = []
        for sg in security_groups:
            for rule in sg.inbound_rules:
                cidr = rule.get("cidr", "")
                if cidr in ("0.0.0.0/0", "::/0"):
                    open_groups.append(sg)
                    break
        return open_groups
