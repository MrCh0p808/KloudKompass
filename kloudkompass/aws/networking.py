# kloudkompass/aws/networking.py
# -----------------------------
# AWS VPC/networking provider implementation. Uses AWS CLI
# ec2 describe-vpcs, describe-subnets, describe-security-groups
# to list and inspect network resources.

from typing import List, Dict, Any, Optional

from kloudkompass.core.networking_base import (
    NetworkProvider, VPCRecord, SubnetRecord, SecurityGroupRecord,
)
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.utils.subprocess_helpers import run_cli_json, build_aws_command
from kloudkompass.utils.logger import debug


class AWSNetworkProvider(NetworkProvider):
    """
    AWS VPC implementation of the NetworkProvider interface.

    Uses `aws ec2 describe-vpcs`, `describe-subnets`, and
    `describe-security-groups` for network resource queries.
    """

    provider_name = "aws"
    cli_command = "aws"

    def is_available(self) -> bool:
        import shutil
        return shutil.which("aws") is not None

    def validate_credentials(self) -> bool:
        from kloudkompass.core.health import check_aws_credentials
        is_valid, _ = check_aws_credentials()
        return is_valid

    def _ensure_ready(self) -> None:
        if not self.is_available():
            raise KloudKompassError(
                "AWS CLI is not installed or not in PATH.",
                suggestion="Install it: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
            )
        if not self.validate_credentials():
            raise KloudKompassError(
                "AWS credentials are not configured or have expired.",
                suggestion="Run 'aws configure' or check your ~/.aws/credentials"
            )

    @staticmethod
    def _extract_name(tags: list) -> str:
        """Extract Name tag value from AWS tags list."""
        for tag in tags:
            if tag.get("Key") == "Name":
                return tag.get("Value", "")
        return ""

    @staticmethod
    def _extract_tags(tags: list) -> Dict[str, str]:
        """Convert AWS tags list to dict."""
        return {t.get("Key", ""): t.get("Value", "") for t in tags}

    def list_vpcs(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[VPCRecord]:
        """List all VPCs using aws ec2 describe-vpcs."""
        self._ensure_ready()
        debug("Fetching VPCs...")

        command = build_aws_command("ec2", "describe-vpcs",
                                    profile=profile, region=region)
                                    
        if tags:
            filter_parts = []
            for key, value in tags.items():
                filter_parts.append(f"Name=tag:{key},Values={value}")
            if filter_parts:
                command.extend(["--filters"] + filter_parts)

        data = run_cli_json(command)
        vpcs: List[VPCRecord] = []

        for vpc_data in data.get("Vpcs", []):
            raw_tags = vpc_data.get("Tags", [])
            vpcs.append(VPCRecord(
                vpc_id=vpc_data.get("VpcId", ""),
                name=self._extract_name(raw_tags) or vpc_data.get("VpcId", ""),
                cidr_block=vpc_data.get("CidrBlock", ""),
                state=vpc_data.get("State", ""),
                region=region or "",
                is_default=vpc_data.get("IsDefault", False),
                tags=self._extract_tags(raw_tags),
            ))

        vpcs.sort(key=lambda v: v.name.lower())
        debug(f"Found {len(vpcs)} VPCs")
        return vpcs

    def list_subnets(
        self,
        vpc_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[SubnetRecord]:
        """List subnets. If vpc_id provided, filter to that VPC."""
        self._ensure_ready()
        debug(f"Fetching subnets{f' for VPC {vpc_id}' if vpc_id else ''}...")

        command = build_aws_command("ec2", "describe-subnets",
                                    profile=profile, region=region)
        filter_parts = []
        if vpc_id:
            filter_parts.append(f"Name=vpc-id,Values={vpc_id}")
            
        if tags:
            for key, value in tags.items():
                filter_parts.append(f"Name=tag:{key},Values={value}")
                
        if filter_parts:
            command.extend(["--filters"] + filter_parts)

        data = run_cli_json(command)
        subnets: List[SubnetRecord] = []

        for subnet_data in data.get("Subnets", []):
            raw_tags = subnet_data.get("Tags", [])
            subnets.append(SubnetRecord(
                subnet_id=subnet_data.get("SubnetId", ""),
                name=self._extract_name(raw_tags) or subnet_data.get("SubnetId", ""),
                vpc_id=subnet_data.get("VpcId", ""),
                cidr_block=subnet_data.get("CidrBlock", ""),
                availability_zone=subnet_data.get("AvailabilityZone", ""),
                available_ips=subnet_data.get("AvailableIpAddressCount", 0),
                is_public=subnet_data.get("MapPublicIpOnLaunch", False),
                tags=self._extract_tags(raw_tags),
            ))

        subnets.sort(key=lambda s: s.availability_zone)
        debug(f"Found {len(subnets)} subnets")
        return subnets

    def list_security_groups(
        self,
        vpc_id: Optional[str] = None,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[SecurityGroupRecord]:
        """List security groups. If vpc_id provided, filter to that VPC."""
        self._ensure_ready()
        debug("Fetching security groups...")

        command = build_aws_command("ec2", "describe-security-groups",
                                    profile=profile, region=region)
        filter_parts = []
        if vpc_id:
            filter_parts.append(f"Name=vpc-id,Values={vpc_id}")
            
        if tags:
            for key, value in tags.items():
                filter_parts.append(f"Name=tag:{key},Values={value}")
                
        if filter_parts:
            command.extend(["--filters"] + filter_parts)

        data = run_cli_json(command)
        groups: List[SecurityGroupRecord] = []

        for sg_data in data.get("SecurityGroups", []):
            raw_tags = sg_data.get("Tags", [])

            inbound_rules = []
            for perm in sg_data.get("IpPermissions", []):
                for ip_range in perm.get("IpRanges", []):
                    inbound_rules.append({
                        "protocol": perm.get("IpProtocol", "-1"),
                        "from_port": perm.get("FromPort", 0),
                        "to_port": perm.get("ToPort", 65535),
                        "cidr": ip_range.get("CidrIp", ""),
                        "description": ip_range.get("Description", ""),
                    })

            outbound_rules = []
            for perm in sg_data.get("IpPermissionsEgress", []):
                for ip_range in perm.get("IpRanges", []):
                    outbound_rules.append({
                        "protocol": perm.get("IpProtocol", "-1"),
                        "from_port": perm.get("FromPort", 0),
                        "to_port": perm.get("ToPort", 65535),
                        "cidr": ip_range.get("CidrIp", ""),
                        "description": ip_range.get("Description", ""),
                    })

            groups.append(SecurityGroupRecord(
                group_id=sg_data.get("GroupId", ""),
                name=sg_data.get("GroupName", ""),
                description=sg_data.get("Description", ""),
                vpc_id=sg_data.get("VpcId", ""),
                inbound_rules=inbound_rules,
                outbound_rules=outbound_rules,
                tags=self._extract_tags(raw_tags),
            ))

        groups.sort(key=lambda g: g.name.lower())
        debug(f"Found {len(groups)} security groups")
        return groups

    def get_security_group_rules(
        self,
        group_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> SecurityGroupRecord:
        """Get detailed rules for a specific security group."""
        self._ensure_ready()

        command = build_aws_command("ec2", "describe-security-groups",
                                    profile=profile, region=region)
        command.extend(["--group-ids", group_id])

        data = run_cli_json(command)
        groups = data.get("SecurityGroups", [])
        if not groups:
            raise KloudKompassError(
                f"Security group {group_id} not found.",
                suggestion="Check that the group ID is correct and you have access."
            )

        # Re-use list_security_groups parsing by wrapping in the expected format
        sg_data = groups[0]
        raw_tags = sg_data.get("Tags", [])

        inbound_rules = []
        for perm in sg_data.get("IpPermissions", []):
            for ip_range in perm.get("IpRanges", []):
                inbound_rules.append({
                    "protocol": perm.get("IpProtocol", "-1"),
                    "from_port": perm.get("FromPort", 0),
                    "to_port": perm.get("ToPort", 65535),
                    "cidr": ip_range.get("CidrIp", ""),
                    "description": ip_range.get("Description", ""),
                })

        outbound_rules = []
        for perm in sg_data.get("IpPermissionsEgress", []):
            for ip_range in perm.get("IpRanges", []):
                outbound_rules.append({
                    "protocol": perm.get("IpProtocol", "-1"),
                    "from_port": perm.get("FromPort", 0),
                    "to_port": perm.get("ToPort", 65535),
                    "cidr": ip_range.get("CidrIp", ""),
                    "description": ip_range.get("Description", ""),
                })

        return SecurityGroupRecord(
            group_id=sg_data.get("GroupId", ""),
            name=sg_data.get("GroupName", ""),
            description=sg_data.get("Description", ""),
            vpc_id=sg_data.get("VpcId", ""),
            inbound_rules=inbound_rules,
            outbound_rules=outbound_rules,
            tags=self._extract_tags(raw_tags),
        )
