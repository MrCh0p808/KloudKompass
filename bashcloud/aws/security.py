# bashcloud/aws/security.py
# --------------------------
# This module will handle AWS security checks like public S3 buckets,
# open security groups, and IAM audit. Stubbed for future expansion.
#
# To expand this module:
# 1. Implement checks for common security issues:
#    - Public S3 buckets (aws s3api get-bucket-acl, get-bucket-policy)
#    - Open security groups (aws ec2 describe-security-groups, filter 0.0.0.0/0)
#    - IAM users without MFA (aws iam list-users, get-login-profile)
#    - Unused access keys (aws iam list-access-keys, get-access-key-last-used)
# 2. Return results in a normalized SecurityFinding format
# 3. Add severity levels (critical, high, medium, low)

from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Security finding severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityFinding:
    """
    Normalized security finding format.
    
    This to represent security issues uniformly across providers.
    The CLI can then format and display findings consistently.
    """
    finding_type: str     # e.g. "public-bucket", "open-security-group"
    resource_id: str      # AWS resource ID
    resource_name: str    # Human readable name
    severity: Severity
    description: str      # What the issue is
    recommendation: str   # How to fix it


class AWSSecurityProvider:
    """
    AWS security checks provider stub.
    
    Implementation planned to common security audits here. Each check method
    returns a list of SecurityFinding objects for any issues found.
    """
    
    provider_name = "AWS"
    cli_command = "aws"
    
    def check_public_s3_buckets(
        self,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Find S3 buckets with public access.
        
        Will check bucket ACLs and policies for public access grants.
        """
        raise NotImplementedError("Public S3 bucket check not yet implemented")
    
    def check_open_security_groups(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Find security groups with overly permissive rules.
        
        Will look for rules allowing 0.0.0.0/0 on sensitive ports.
        """
        raise NotImplementedError("Open security group check not yet implemented")
    
    def check_iam_mfa_status(
        self,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Find IAM users without MFA enabled.
        
        Users with console access should have MFA enabled.
        """
        raise NotImplementedError("IAM MFA check not yet implemented")
    
    def run_all_checks(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Run all security checks and return combined findings.
        """
        raise NotImplementedError("Security checks not yet implemented")
