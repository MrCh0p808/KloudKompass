# kloudkompass/aws/storage.py
# --------------------------
# AWS S3 and EBS storage provider implementation. Uses AWS CLI
# s3api list-buckets and ec2 describe-volumes to list storage resources.

from typing import List, Dict, Any, Optional

from kloudkompass.core.storage_base import StorageProvider, BucketRecord, VolumeRecord
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.utils.subprocess_helpers import run_cli_json, build_aws_command
from kloudkompass.utils.logger import debug


class AWSStorageProvider(StorageProvider):
    """
    AWS S3/EBS implementation of the StorageProvider interface.

    Uses `aws s3api list-buckets` for object storage and
    `aws ec2 describe-volumes` for block storage.
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

    def get_manifest(self) -> Dict[str, Any]:
        """Return the module manifest for the Adaptive Sidebar."""
        return {
            "storage": {
                "label": "Storage (S3/EBS)",
                "icon": "🗄️"
            }
        }

    @staticmethod
    def _extract_tags(tags: list) -> Dict[str, str]:
        """Convert AWS tags list to dict."""
        return {t.get("Key", ""): t.get("Value", "") for t in tags}

    @staticmethod
    def _extract_name(tags: list) -> str:
        """Extract Name tag value."""
        for tag in tags:
            if tag.get("Key") == "Name":
                return tag.get("Value", "")
        return ""

    def list_buckets(
        self,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[BucketRecord]:
        """List all S3 buckets using aws s3api list-buckets."""
        self._ensure_ready()
        debug("Fetching S3 buckets...")

        command = build_aws_command("s3api", "list-buckets", profile=profile)
        data = run_cli_json(command)
        buckets: List[BucketRecord] = []

        for bucket_data in data.get("Buckets", []):
            bucket_name = bucket_data.get("Name", "")
            
            # Skip if tags requested (not supported yet)
            if tags:
                continue
                
            region = ""
            access_level = "unknown"
            
            # Apply filters if present
            if filters:
                target_region = filters.get("region")
                if target_region:
                    # Fetch location
                    loc_cmd = build_aws_command("s3api", "get-bucket-location", 
                                                args={"bucket": bucket_name}, profile=profile)
                    try:
                        loc_data = run_cli_json(loc_cmd)
                        region = loc_data.get("LocationConstraint") or "us-east-1"
                    except KloudKompassError:
                        region = "unknown"
                        
                    if target_region.lower() not in region.lower() and region != "unknown":
                        continue
                        
                target_public = filters.get("public-access")
                if target_public:
                    # Check policy status
                    pol_cmd = build_aws_command("s3api", "get-bucket-policy-status", 
                                                args={"bucket": bucket_name}, profile=profile)
                    try:
                        pol_data = run_cli_json(pol_cmd)
                        is_public = pol_data.get("PolicyStatus", {}).get("IsPublic", False)
                        access_level = "public" if is_public else "private"
                    except KloudKompassError:
                        is_public = False
                        access_level = "private"
                        
                    if target_public.lower() == "public" and not is_public:
                        continue
                    if target_public.lower() == "private" and is_public:
                        continue
                
            buckets.append(BucketRecord(
                bucket_name=bucket_name,
                region=region,
                access_level=access_level,
                creation_date=bucket_data.get("CreationDate", ""),
            ))

        buckets.sort(key=lambda b: b.bucket_name.lower())
        debug(f"Found {len(buckets)} S3 buckets")
        return buckets

    def list_volumes(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[VolumeRecord]:
        """List EBS volumes using aws ec2 describe-volumes."""
        self._ensure_ready()
        debug("Fetching EBS volumes...")

        command = build_aws_command("ec2", "describe-volumes",
                                    profile=profile, region=region)

        filter_parts = []
        if filters:
            for key, value in filters.items():
                filter_parts.append(f"Name={key},Values={value}")
                
        if tags:
            for key, value in tags.items():
                filter_parts.append(f"Name=tag:{key},Values={value}")
                
        if filter_parts:
            command.extend(["--filters"] + filter_parts)

        data = run_cli_json(command)
        volumes: List[VolumeRecord] = []

        for vol_data in data.get("Volumes", []):
            raw_tags = vol_data.get("Tags", [])

            # Check attachment status
            attached_to = ""
            attachments = vol_data.get("Attachments", [])
            if attachments:
                attached_to = attachments[0].get("InstanceId", "")

            volumes.append(VolumeRecord(
                volume_id=vol_data.get("VolumeId", ""),
                name=self._extract_name(raw_tags) or vol_data.get("VolumeId", ""),
                size_gb=vol_data.get("Size", 0),
                volume_type=vol_data.get("VolumeType", ""),
                state=vol_data.get("State", ""),
                attached_to=attached_to,
                region=vol_data.get("AvailabilityZone", ""),
                encrypted=vol_data.get("Encrypted", False),
                tags=self._extract_tags(raw_tags),
            ))

        volumes.sort(key=lambda v: v.name.lower())
        debug(f"Found {len(volumes)} EBS volumes")
        return volumes
