# kloudkompass/core/storage_base.py
# --------------------------------
# Abstract base for storage resource queries. All cloud-specific
# storage modules (S3/EBS, Azure Blob/Disk, GCS) inherit from this.

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from kloudkompass.core.provider_base import ProviderBase


@dataclass
class BucketRecord:
    """Normalized object storage bucket record (S3, Azure Blob, GCS)."""
    bucket_name: str
    region: str = ""
    creation_date: str = ""
    access_level: str = ""    # private, public-read, etc.
    storage_class: str = ""   # STANDARD, GLACIER, etc.
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bucket_name": self.bucket_name,
            "region": self.region,
            "creation_date": self.creation_date,
            "access_level": self.access_level,
            "storage_class": self.storage_class,
            "tags": self.tags,
        }


@dataclass
class VolumeRecord:
    """Normalized block storage volume record (EBS, Azure Disk, PD)."""
    volume_id: str
    name: str = ""
    size_gb: int = 0
    volume_type: str = ""     # gp3, io2, Standard_LRS, etc.
    state: str = ""           # available, in-use, etc.
    attached_to: str = ""     # Instance ID if attached
    region: str = ""
    encrypted: bool = False
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "volume_id": self.volume_id,
            "name": self.name,
            "size_gb": self.size_gb,
            "volume_type": self.volume_type,
            "state": self.state,
            "attached_to": self.attached_to,
            "region": self.region,
            "encrypted": self.encrypted,
            "tags": self.tags,
        }


class StorageProvider(ProviderBase):
    """
    Abstract base for storage resource operations.

    Each cloud provider implements these methods to list buckets and
    block storage volumes.
    """

    @abstractmethod
    def list_buckets(
        self,
        profile: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, str]] = None,
    ) -> List[BucketRecord]:
        """List all object storage buckets."""
        pass

    @abstractmethod
    def list_volumes(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
        filters: Optional[Dict[str, str]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> List[VolumeRecord]:
        """
        List block storage volumes.

        Args:
            filters: Key-value filters (e.g., {"state": "available"}).
        """
        pass

    def find_unattached_volumes(
        self,
        volumes: List[VolumeRecord],
    ) -> List[VolumeRecord]:
        """Find volumes not attached to any instance (waste detection)."""
        return [v for v in volumes if v.state.lower() == "available" and not v.attached_to]

    def find_unencrypted_volumes(
        self,
        volumes: List[VolumeRecord],
    ) -> List[VolumeRecord]:
        """Find unencrypted volumes (security check)."""
        return [v for v in volumes if not v.encrypted]
