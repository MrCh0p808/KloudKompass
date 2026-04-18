from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import base64
import time
from datetime import datetime, timezone

from kloudkompass.utils.subprocess_helpers import run_cli_json, build_aws_command, run_cli_command
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.core.security_base import SecurityProvider, SecurityFinding, Severity





class AWSSecurityProvider(SecurityProvider):
    """
    AWS security checks provider.
    """
    
    provider_name = "AWS"
    cli_command = "aws"
    
    def check_public_buckets(
        self,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Find S3 buckets with public access by checking policy status.
        """
        findings = []
        try:
            # 1. List all buckets
            list_cmd = build_aws_command("s3api", "list-buckets", profile=profile)
            data = run_cli_json(list_cmd)
            
            for bucket in data.get("Buckets", []):
                name = bucket.get("Name", "")
                
                # 2. Check policy status (Best indicator of effective public access)
                try:
                    status_cmd = build_aws_command("s3api", "get-bucket-policy-status", 
                                                   args={"bucket": name}, profile=profile)
                    status_data = run_cli_json(status_cmd)
                    if status_data.get("PolicyStatus", {}).get("IsPublic"):
                        findings.append(SecurityFinding(
                            finding_type="public-s3-bucket",
                            resource_id=name,
                            resource_name=name,
                            severity=Severity.HIGH,
                            description=f"Bucket '{name}' has a policy that makes it publicly accessible.",
                            recommendation="Review the bucket policy and enable S3 Block Public Access."
                        ))
                except KloudKompassError:
                    # Often means no policy exists, which is fine
                    pass
        except KloudKompassError:
            pass
            
        return findings
    
    def check_open_security_groups(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Find security groups allowing 0.0.0.0/0 on sensitive ports.
        """
        findings = []
        # SENSITIVE_PORTS = [22, 3389, 21, 23, 1433, 3306, 5432, 6379, 9200]
        try:
            command = build_aws_command("ec2", "describe-security-groups", 
                                        profile=profile, region=region)
            data = run_cli_json(command)
            
            for sg in data.get("SecurityGroups", []):
                sg_id = sg.get("GroupId", "")
                sg_name = sg.get("GroupName", "")
                
                for perm in sg.get("IpPermissions", []):
                    # Check for IPv4 0.0.0.0/0
                    is_public = any(r.get("CidrIp") == "0.0.0.0/0" for r in perm.get("IpRanges", []))
                    # Check for IPv6 ::/0
                    is_public = is_public or any(r.get("CidrIpv6") == "::/0" for r in perm.get("Ipv6Ranges", []))
                    
                    if is_public:
                        from_port = perm.get("FromPort", -1)
                        to_port = perm.get("ToPort", -1)
                        protocol = perm.get("IpProtocol", "")
                        
                        desc = f"Security Group allows '{protocol}' traffic from anywhere (0.0.0.0/0 or ::/0)"
                        if from_port != -1:
                            desc += f" on ports {from_port}-{to_port}"
                        
                        severity = Severity.MEDIUM
                        # Escalate for common management ports
                        if from_port in [22, 3389]:
                            severity = Severity.HIGH
                        elif protocol == "-1": # All traffic
                            severity = Severity.CRITICAL
                            
                        findings.append(SecurityFinding(
                            finding_type="open-security-group",
                            resource_id=sg_id,
                            resource_name=sg_name,
                            severity=severity,
                            description=desc,
                            recommendation="Restrict access to specific CIDR ranges or your office IP."
                        ))
        except KloudKompassError:
            pass

        return findings
    
    def check_iam_mfa(
        self,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Find IAM users with passwords but without MFA enabled using credential reports.
        """
        findings = []
        try:
            # 1. Request report generation
            gen_cmd = build_aws_command("iam", "generate-credential-report", profile=profile)
            run_cli_json(gen_cmd)
            
            # 2. Poll for completion (usually instant, but let's be safe)
            report = None
            for _ in range(5):
                try:
                    get_cmd = build_aws_command("iam", "get-credential-report", profile=profile)
                    report = run_cli_json(get_cmd)
                    break
                except KloudKompassError:
                    time.sleep(2)
            
            if not report or "Content" not in report:
                return []
                
            # 3. Parse CSV content
            import csv
            import io
            csv_content = base64.b64decode(report["Content"]).decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_content))
            
            for row in reader:
                user = row.get("user")
                has_password = row.get("password_enabled") == "true"
                mfa_active = row.get("mfa_active") == "true"
                
                if has_password and not mfa_active:
                    findings.append(SecurityFinding(
                        finding_type="iam-user-no-mfa",
                        resource_id=user,
                        resource_name=user,
                        severity=Severity.HIGH,
                        description=f"User '{user}' has console access but MFA is NOT enabled.",
                        recommendation="Enforce MFA for all users with console access."
                    ))
        except Exception:
            pass
            
        return findings

    def check_unused_access_keys(
        self,
        max_age_days: int = 90,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Find access keys not used within max_age_days."""
        findings = []
        try:
            gen_cmd = build_aws_command("iam", "generate-credential-report", profile=profile)
            run_cli_json(gen_cmd)
            
            report = None
            for _ in range(5):
                try:
                    get_cmd = build_aws_command("iam", "get-credential-report", profile=profile)
                    report = run_cli_json(get_cmd)
                    break
                except KloudKompassError:
                    time.sleep(2)
            
            if not report or "Content" not in report:
                return []
                
            import csv
            import io
            csv_content = base64.b64decode(report["Content"]).decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_content))
            now = datetime.now(timezone.utc)
            
            for row in reader:
                user = row.get("user")
                if user == "<root_account>":
                    continue
                    
                for i in [1, 2]:
                    active = row.get(f"access_key_{i}_active") == "true"
                    if not active:
                        continue
                        
                    last_used_str = row.get(f"access_key_{i}_last_used_date", "N/A")
                    last_rotated_str = row.get(f"access_key_{i}_last_rotated", "N/A")
                    
                    target_date_str = last_used_str if last_used_str != "N/A" else last_rotated_str
                    if target_date_str and target_date_str != "N/A":
                        try:
                            # Format usually like 2026-03-02T12:00:00+00:00
                            td = datetime.fromisoformat(target_date_str.replace('Z', '+00:00'))
                            age_days = (now - td).days
                            if age_days > max_age_days:
                                findings.append(SecurityFinding(
                                    finding_type="unused-access-key",
                                    resource_id=user,
                                    resource_name=user,
                                    severity=Severity.MEDIUM,
                                    description=f"User '{user}' has an active access key ({i}) unused for {age_days} days.",
                                    recommendation="Deactivate or rotate this access key to reduce attack surface.",
                                    remediation_cmd=f"aws iam update-access-key --user-name {user} --access-key-id <KEY_ID> --status Inactive"
                                ))
                        except ValueError:
                            pass
        except Exception:
            pass
            
        return findings

    def check_encryption(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Find unencrypted storage volumes and databases."""
        findings = []
        try:
            # 1. EBS Volumes
            ebs_cmd = build_aws_command("ec2", "describe-volumes", profile=profile, region=region)
            ebs_data = run_cli_json(ebs_cmd)
            for vol in ebs_data.get("Volumes", []):
                if not vol.get("Encrypted", False):
                    vid = vol.get("VolumeId", "")
                    findings.append(SecurityFinding(
                        finding_type="unencrypted-ebs",
                        resource_id=vid,
                        resource_name=vid,
                        severity=Severity.HIGH,
                        description=f"EBS Volume '{vid}' is unencrypted.",
                        recommendation="Migrate the volume to an encrypted copy."
                    ))
        except KloudKompassError:
            pass
            
        try:
            # 2. RDS Instances
            rds_cmd = build_aws_command("rds", "describe-db-instances", profile=profile, region=region)
            rds_data = run_cli_json(rds_cmd)
            for db in rds_data.get("DBInstances", []):
                if not db.get("StorageEncrypted", False):
                    dbid = db.get("DBInstanceIdentifier", "")
                    findings.append(SecurityFinding(
                        finding_type="unencrypted-rds",
                        resource_id=dbid,
                        resource_name=dbid,
                        severity=Severity.HIGH,
                        description=f"RDS Instance '{dbid}' has unencrypted storage.",
                        recommendation="Migrate the database to an encrypted copy using snapshots."
                    ))
        except KloudKompassError:
            pass
            
        return findings
    
    def run_all_checks(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Run all security checks and return combined findings.
        """
        all_findings = super().run_all_checks(region=region, profile=profile)
        return all_findings
