# kloudkompass/aws/compute.py
# --------------------------
# AWS EC2 compute provider implementation. Uses the AWS CLI
# ec2 describe-instances command to list and manage EC2 instances.
# All results are normalized to ComputeInstance records.

from typing import List, Dict, Any, Optional

from kloudkompass.core.compute_base import ComputeProvider, ComputeInstance
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.utils.subprocess_helpers import run_cli_json, build_aws_command, run_cli_command
from kloudkompass.utils.parsers import safe_get_nested
from kloudkompass.utils.logger import debug


class AWSComputeProvider(ComputeProvider):
    """
    AWS EC2 implementation of the ComputeProvider interface.

    Uses `aws ec2 describe-instances` to list instances and
    `aws ec2 start/stop/reboot-instances` for lifecycle operations.
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
        """Verify CLI and credentials before making API calls."""
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

    def _parse_instance(self, instance_data: Dict[str, Any]) -> ComputeInstance:
        """Parse a single EC2 instance from the AWS API response."""
        # Extract name from tags
        name = ""
        tags_dict: Dict[str, str] = {}
        for tag in instance_data.get("Tags", []):
            key = tag.get("Key", "")
            value = tag.get("Value", "")
            tags_dict[key] = value
            if key == "Name":
                name = value

        return ComputeInstance(
            instance_id=instance_data.get("InstanceId", ""),
            name=name or instance_data.get("InstanceId", ""),
            instance_type=instance_data.get("InstanceType", ""),
            state=safe_get_nested(instance_data, "State", "Name") or "unknown",
            region=safe_get_nested(instance_data, "Placement", "AvailabilityZone") or "",
            public_ip=instance_data.get("PublicIpAddress", ""),
            private_ip=instance_data.get("PrivateIpAddress", ""),
            launch_time=instance_data.get("LaunchTime", ""),
            platform=instance_data.get("PlatformDetails", "Linux/UNIX"),
            vpc_id=instance_data.get("VpcId", ""),
            tags=tags_dict,
            raw_data=instance_data,
        )

    def list_instances(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[ComputeInstance]:
        """
        List all EC2 instances using aws ec2 describe-instances.

        Supports filtering by state via `filters` dict, and
        tag-based filtering via `tags` dict.
        """
        self._ensure_ready()
        debug("Fetching EC2 instances...")

        command = build_aws_command("ec2", "describe-instances",
                                    profile=profile, region=region)

        # Add filters if provided
        filter_parts = []
        if filters:
            for key, value in filters.items():
                filter_parts.append(f"Name={key},Values={value}")
                
        # Add explicit tags as filters
        if tags:
            for key, value in tags.items():
                filter_parts.append(f"Name=tag:{key},Values={value}")
                
        if filter_parts:
            command.extend(["--filters"] + filter_parts)

        data = run_cli_json(command)
        instances: List[ComputeInstance] = []

        for reservation in data.get("Reservations", []):
            for instance_data in reservation.get("Instances", []):
                instances.append(self._parse_instance(instance_data))

        # Sort by name
        instances.sort(key=lambda i: i.name.lower())
        debug(f"Found {len(instances)} EC2 instances")
        return instances

    def get_instance(
        self,
        instance_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> Optional[ComputeInstance]:
        """Get details for a single EC2 instance."""
        self._ensure_ready()

        command = build_aws_command("ec2", "describe-instances",
                                    profile=profile, region=region)
        command.extend(["--instance-ids", instance_id])

        try:
            data = run_cli_json(command)
            for reservation in data.get("Reservations", []):
                for instance_data in reservation.get("Instances", []):
                    return self._parse_instance(instance_data)
        except KloudKompassError:
            return None
        return None

    def start_instance(
        self,
        instance_ids: List[str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Start stopped EC2 instances."""
        self._ensure_ready()
        debug(f"Starting instances {instance_ids}...")

        command = build_aws_command("ec2", "start-instances",
                                    profile=profile, region=region)
        command.extend(["--instance-ids"])
        command.extend(instance_ids)

        try:
            run_cli_json(command)
            return True
        except KloudKompassError:
            return False

    def stop_instance(
        self,
        instance_ids: List[str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Stop running EC2 instances."""
        self._ensure_ready()
        debug(f"Stopping instances {instance_ids}...")

        command = build_aws_command("ec2", "stop-instances",
                                    profile=profile, region=region)
        command.extend(["--instance-ids"])
        command.extend(instance_ids)

        try:
            run_cli_json(command)
            return True
        except KloudKompassError:
            return False

    def terminate_instance(
        self,
        instance_ids: List[str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Terminate EC2 instances."""
        self._ensure_ready()
        debug(f"Terminating instances {instance_ids}...")

        command = build_aws_command("ec2", "terminate-instances",
                                    profile=profile, region=region)
        command.extend(["--instance-ids"])
        command.extend(instance_ids)

        try:
            run_cli_json(command)
            return True
        except KloudKompassError:
            return False

    def reboot_instance(
        self,
        instance_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Reboot a running EC2 instance."""
        self._ensure_ready()
        debug(f"Rebooting instance {instance_id}...")

        command = build_aws_command("ec2", "reboot-instances",
                                    profile=profile, region=region)
        command.extend(["--instance-ids", instance_id])

        try:
            run_cli_json(command)
            return True
        except KloudKompassError:
            return False

    def add_tags(
        self,
        resource_ids: List[str],
        tags: Dict[str, str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Add or update tags on specified resources."""
        self._ensure_ready()
        if not resource_ids or not tags:
            return False
            
        debug(f"Adding tags to {len(resource_ids)} resources...")
        command = build_aws_command("ec2", "create-tags",
                                    profile=profile, region=region)
        command.extend(["--resources"] + resource_ids)
        
        tag_args = []
        for k, v in tags.items():
            tag_args.append(f"Key={k},Value={v}")
        command.extend(["--tags"] + tag_args)
        
        try:
            run_cli_command(command)
            return True
        except KloudKompassError:
            return False

    def remove_tags(
        self,
        resource_ids: List[str],
        tag_keys: List[str],
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        """Remove tags from specified resources."""
        self._ensure_ready()
        if not resource_ids or not tag_keys:
            return False
            
        debug(f"Removing tags from {len(resource_ids)} resources...")
        command = build_aws_command("ec2", "delete-tags",
                                    profile=profile, region=region)
        command.extend(["--resources"] + resource_ids)
        
        tag_args = []
        for k in tag_keys:
            tag_args.append(f"Key={k}")
        command.extend(["--tags"] + tag_args)
        
        try:
            run_cli_command(command)
            return True
        except KloudKompassError:
            return False
