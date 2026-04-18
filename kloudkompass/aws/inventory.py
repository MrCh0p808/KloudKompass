# kloudkompass/aws/inventory.py
# ---------------------------
# This module will handle AWS compute and storage inventory queries.
# it stubbed with the structure in place. The implementation
# follows the same pattern as cost.py: validate -> build command -> run -> parse.
#
# To expand this module:
# 1. Create an AWSInventoryProvider class following the same pattern as AWSCostProvider
# 2. Implement methods for EC2 instances, S3 buckets, EBS volumes, etc.
# 3. Use aws ec2 describe-instances, aws s3 ls, etc. via subprocess
# 4. Parse responses into a normalized InventoryRecord format
# 5. Add pagination handling for large inventories

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class InventoryRecord:
    """
    Normalized inventory record format.
    
    Uses this to represent resources from any provider uniformly.
    The fields here are placeholders - expand based on actual needs.
    """
    resource_type: str    # e.g. "ec2-instance", "s3-bucket"
    resource_id: str      # AWS resource ID
    name: str             # Name tag or identifier
    region: str           # AWS region
    state: str            # Running, stopped, available, etc.
    details: dict         # Additional resource-specific details


class AWSInventoryProvider:
    """
    AWS inventory provider stub.
    
    Implementation planned to this to fetch EC2 instances, S3 buckets, and other
    resources. The structure mirrors AWSCostProvider for consistency.
    """
    
    provider_name = "AWS"
    cli_command = "aws"
    
    def list_ec2_instances(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[InventoryRecord]:
        """
        List EC2 instances.
        
        Uses: aws ec2 describe-instances --output json
        Then parse and return as InventoryRecords.
        """
        raise NotImplementedError("EC2 inventory not yet implemented")
    
    def list_s3_buckets(
        self,
        profile: Optional[str] = None,
    ) -> List[InventoryRecord]:
        """
        List S3 buckets.
        
        Uses: aws s3api list-buckets --output json
        """
        raise NotImplementedError("S3 inventory not yet implemented")
    
    def list_rds_instances(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[InventoryRecord]:
        """
        List RDS database instances.
        
        Uses: aws rds describe-db-instances --output json
        """
        raise NotImplementedError("RDS inventory not yet implemented")
