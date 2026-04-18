# kloudkompass/core/security_base.py
# ---------------------------------
# Abstract base for security audit providers. All cloud-specific
# security modules inherit from this. Standardized SecurityFinding
# format ensures the CLI/TUI can display security issues uniformly.

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from kloudkompass.core.provider_base import ProviderBase


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

    Represents security issues uniformly across providers.
    The CLI/TUI format and display findings consistently.
    """
    finding_type: str       # e.g. "public-bucket", "open-security-group"
    resource_id: str        # Cloud resource ID
    resource_name: str      # Human readable name
    severity: Severity
    description: str        # What the issue is
    recommendation: str     # How to fix it
    remediation_cmd: str = ""  # Exact CLI command to fix (if applicable)
    region: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_type": self.finding_type,
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "severity": self.severity.value,
            "description": self.description,
            "recommendation": self.recommendation,
            "remediation_cmd": self.remediation_cmd,
            "region": self.region,
        }


# Scoring weights for security score calculation
_SEVERITY_WEIGHTS = {
    Severity.CRITICAL: 10,
    Severity.HIGH: 5,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
    Severity.INFO: 0,
}


class SecurityProvider(ProviderBase):
    """
    Abstract base for security audit operations.

    Each cloud provider implements these methods to scan for
    common security misconfigurations.
    """

    @abstractmethod
    def check_public_buckets(
        self,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Find object storage buckets with public access."""
        pass

    @abstractmethod
    def check_open_security_groups(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Find security groups/NSGs with overly permissive rules."""
        pass

    @abstractmethod
    def check_iam_mfa(
        self,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Find IAM users without MFA enabled."""
        pass

    @abstractmethod
    def check_unused_access_keys(
        self,
        max_age_days: int = 90,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Find access keys not used within max_age_days."""
        pass

    @abstractmethod
    def check_encryption(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """Find unencrypted storage volumes and database instances."""
        pass

    def run_all_checks(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[SecurityFinding]:
        """
        Run all security checks and return combined findings.

        Sorted by severity (CRITICAL first, then HIGH, MEDIUM, LOW, INFO).
        """
        findings: List[SecurityFinding] = []
        findings.extend(self.check_public_buckets(profile))
        findings.extend(self.check_open_security_groups(region, profile))
        findings.extend(self.check_iam_mfa(profile))
        findings.extend(self.check_unused_access_keys(profile=profile))
        findings.extend(self.check_encryption(region, profile))

        # Sort by severity weight descending
        severity_order = {s: i for i, s in enumerate(Severity)}
        findings.sort(key=lambda f: severity_order.get(f.severity, 99))
        return findings

    @staticmethod
    def calculate_security_score(findings: List[SecurityFinding]) -> int:
        """
        Calculate a security score from 0 (terrible) to 100 (perfect).

        Score = max(0, 100 - sum(severity_weights)).
        A clean account with no findings scores 100.
        """
        total_weight = sum(
            _SEVERITY_WEIGHTS.get(f.severity, 0) for f in findings
        )
        return max(0, 100 - total_weight)

    @staticmethod
    def group_by_severity(
        findings: List[SecurityFinding],
    ) -> Dict[str, List[SecurityFinding]]:
        """Group findings by severity level."""
        grouped: Dict[str, List[SecurityFinding]] = {}
        for severity in Severity:
            matches = [f for f in findings if f.severity == severity]
            if matches:
                grouped[severity.value] = matches
        return grouped
