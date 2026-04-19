# kloudkompass/aws/iam.py
# ----------------------
# AWS IAM provider implementation. Uses AWS CLI iam commands
# to list users, roles, and policies.

from typing import List, Dict, Any, Optional

from kloudkompass.core.iam_base import (
    IAMProvider, IAMUserRecord, IAMRoleRecord, IAMPolicyRecord,
)
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.utils.subprocess_helpers import run_cli_json, build_aws_command
from kloudkompass.utils.logger import debug

import base64
import csv
import io
import time


class AWSIAMProvider(IAMProvider):
    """
    AWS IAM implementation of the IAMProvider interface.

    Uses `aws iam list-users`, `list-roles`, and `list-policies`
    for identity and access management queries.
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
            "iam": {
                "label": "Identity (IAM)",
                "icon": "🔐"
            }
        }

    def _get_credential_report(self, profile: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Generate and fetch the IAM credential report to avoid N+1 queries.
        """
        try:
            # Request report generation
            run_cli_json(build_aws_command("iam", "generate-credential-report", profile=profile))
            
            # Poll for readiness (max 10s)
            for _ in range(5):
                try:
                    report = run_cli_json(build_aws_command("iam", "get-credential-report", profile=profile))
                    if "Content" in report:
                        csv_content = base64.b64decode(report["Content"]).decode('utf-8')
                        reader = csv.DictReader(io.StringIO(csv_content))
                        return list(reader)
                except KloudKompassError:
                    time.sleep(2)
        except Exception as e:
            debug(f"Failed to fetch credential report: {e}")
        return []

    def _check_user_mfa(self, user_name: str, profile: Optional[str] = None) -> bool:
        """Fallback MFA check (expensive)."""
        try:
            command = build_aws_command("iam", "list-mfa-devices", profile=profile)
            command.extend(["--user-name", user_name])
            data = run_cli_json(command)
            return len(data.get("MFADevices", [])) > 0
        except KloudKompassError:
            return False

    def _count_access_keys(self, user_name: str, profile: Optional[str] = None) -> int:
        """Fallback access key check (expensive)."""
        try:
            command = build_aws_command("iam", "list-access-keys", profile=profile)
            command.extend(["--user-name", user_name])
            data = run_cli_json(command)
            return len(data.get("AccessKeyMetadata", []))
        except KloudKompassError:
            return 0

    def list_users(
        self,
        profile: Optional[str] = None,
    ) -> List[IAMUserRecord]:
        """List all IAM users with MFA and access key status."""
        self._ensure_ready()
        debug("Fetching IAM users...")

        command = build_aws_command("iam", "list-users", profile=profile)
        data = run_cli_json(command)
        
        # Optimized: Fetch credential report once
        report_rows = self._get_credential_report(profile)
        report_map = {row['user']: row for row in report_rows if 'user' in row}
        
        users: List[IAMUserRecord] = []
        for user_data in data.get("Users", []):
            user_name = user_data.get("UserName", "")
            
            # Extract MFA and Access Key count from report if available
            mfa_enabled = False
            access_keys = 0
            
            if user_name in report_map:
                row = report_map[user_name]
                mfa_enabled = row.get("mfa_active") == "true"
                # Count active access keys
                if row.get("access_key_1_active") == "true": access_keys += 1
                if row.get("access_key_2_active") == "true": access_keys += 1
            else:
                # Fallback to expensive individual calls if report is missing user
                mfa_enabled = self._check_user_mfa(user_name, profile)
                access_keys = self._count_access_keys(user_name, profile)

            users.append(IAMUserRecord(
                user_name=user_name,
                user_id=user_data.get("UserId", ""),
                arn=user_data.get("Arn", ""),
                create_date=user_data.get("CreateDate", ""),
                last_login=user_data.get("PasswordLastUsed", "Never"),
                mfa_enabled=mfa_enabled,
                access_keys=access_keys,
            ))

        users.sort(key=lambda u: u.user_name.lower())
        debug(f"Found {len(users)} IAM users")
        return users

    def list_roles(
        self,
        profile: Optional[str] = None,
    ) -> List[IAMRoleRecord]:
        """List all IAM roles."""
        self._ensure_ready()
        debug("Fetching IAM roles...")

        command = build_aws_command("iam", "list-roles", profile=profile)
        data = run_cli_json(command)
        roles: List[IAMRoleRecord] = []

        for role_data in data.get("Roles", []):
            roles.append(IAMRoleRecord(
                role_name=role_data.get("RoleName", ""),
                role_id=role_data.get("RoleId", ""),
                arn=role_data.get("Arn", ""),
                create_date=role_data.get("CreateDate", ""),
                description=role_data.get("Description", ""),
                max_session_duration=role_data.get("MaxSessionDuration", 3600),
                trust_policy=role_data.get("AssumeRolePolicyDocument", {}),
            ))

        roles.sort(key=lambda r: r.role_name.lower())
        debug(f"Found {len(roles)} IAM roles")
        return roles

    def list_policies(
        self,
        scope: str = "Local",
        profile: Optional[str] = None,
    ) -> List[IAMPolicyRecord]:
        """
        List IAM policies.

        scope: "Local" for customer-managed, "AWS" for AWS-managed.
        """
        self._ensure_ready()
        debug(f"Fetching IAM policies (scope={scope})...")

        command = build_aws_command("iam", "list-policies", profile=profile)
        command.extend(["--scope", scope])
        data = run_cli_json(command)
        policies: List[IAMPolicyRecord] = []

        for policy_data in data.get("Policies", []):
            arn = policy_data.get("Arn", "")
            policies.append(IAMPolicyRecord(
                policy_name=policy_data.get("PolicyName", ""),
                policy_id=policy_data.get("PolicyId", ""),
                arn=arn,
                attachment_count=policy_data.get("AttachmentCount", 0),
                is_aws_managed=arn.startswith("arn:aws:iam::aws:"),
                create_date=policy_data.get("CreateDate", ""),
                description=policy_data.get("Description", ""),
            ))

        policies.sort(key=lambda p: p.policy_name.lower())
        debug(f"Found {len(policies)} IAM policies")
        return policies
