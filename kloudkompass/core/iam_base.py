# kloudkompass/core/iam_base.py
# ----------------------------
# Abstract base for IAM resource queries. All cloud-specific
# IAM modules inherit from this. Normalized output ensures
# the CLI/TUI can display identity resources from any provider.

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from kloudkompass.core.provider_base import ProviderBase


@dataclass
class IAMUserRecord:
    """Normalized IAM user record."""
    user_name: str
    user_id: str
    arn: str = ""
    create_date: str = ""
    last_login: str = ""
    mfa_enabled: bool = False
    access_keys: int = 0
    groups: List[str] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_name": self.user_name,
            "user_id": self.user_id,
            "arn": self.arn,
            "create_date": self.create_date,
            "last_login": self.last_login,
            "mfa_enabled": self.mfa_enabled,
            "access_keys": self.access_keys,
            "groups": self.groups,
            "tags": self.tags,
        }


@dataclass
class IAMRoleRecord:
    """Normalized IAM role record."""
    role_name: str
    role_id: str
    arn: str = ""
    create_date: str = ""
    description: str = ""
    max_session_duration: int = 3600
    trust_policy: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_name": self.role_name,
            "role_id": self.role_id,
            "arn": self.arn,
            "create_date": self.create_date,
            "description": self.description,
            "max_session_duration": self.max_session_duration,
            "trust_policy": self.trust_policy,
            "tags": self.tags,
        }


@dataclass
class IAMPolicyRecord:
    """Normalized IAM policy record."""
    policy_name: str
    policy_id: str
    arn: str = ""
    attachment_count: int = 0
    is_aws_managed: bool = False
    create_date: str = ""
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "policy_id": self.policy_id,
            "arn": self.arn,
            "attachment_count": self.attachment_count,
            "is_aws_managed": self.is_aws_managed,
            "create_date": self.create_date,
            "description": self.description,
        }


class IAMProvider(ProviderBase):
    """
    Abstract base for IAM resource queries.

    Each cloud provider implements these methods to list users, roles,
    and policies.
    """

    @abstractmethod
    def list_users(
        self,
        profile: Optional[str] = None,
    ) -> List[IAMUserRecord]:
        """List all IAM users."""
        pass

    @abstractmethod
    def list_roles(
        self,
        profile: Optional[str] = None,
    ) -> List[IAMRoleRecord]:
        """List all IAM roles."""
        pass

    @abstractmethod
    def list_policies(
        self,
        scope: str = "Local",
        profile: Optional[str] = None,
    ) -> List[IAMPolicyRecord]:
        """
        List IAM policies.

        Args:
            scope: "Local" for customer-managed, "AWS" for AWS-managed.
        """
        pass

    def find_users_without_mfa(
        self,
        users: List[IAMUserRecord],
    ) -> List[IAMUserRecord]:
        """Find users without MFA enabled (security check)."""
        return [u for u in users if not u.mfa_enabled]
