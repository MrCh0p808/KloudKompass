# kloudkompass/core/database_base.py
# ---------------------------------
# Abstract base for database resource queries. All cloud-specific
# database modules (RDS, Azure SQL, Cloud SQL) inherit from this.

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from kloudkompass.core.provider_base import ProviderBase


@dataclass
class DBInstanceRecord:
    """Normalized database instance record."""
    db_id: str             # DB instance identifier
    engine: str            # mysql, postgres, aurora, sqlserver, etc.
    engine_version: str = ""
    instance_class: str = ""   # db.t3.micro, etc.
    status: str = ""       # available, creating, deleting, etc.
    region: str = ""
    endpoint: str = ""     # Connection endpoint
    port: int = 0
    storage_gb: int = 0
    multi_az: bool = False
    encrypted: bool = False
    publicly_accessible: bool = False
    backup_retention_days: int = 0
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "db_id": self.db_id,
            "engine": self.engine,
            "engine_version": self.engine_version,
            "instance_class": self.instance_class,
            "status": self.status,
            "region": self.region,
            "endpoint": self.endpoint,
            "port": self.port,
            "storage_gb": self.storage_gb,
            "multi_az": self.multi_az,
            "encrypted": self.encrypted,
            "publicly_accessible": self.publicly_accessible,
            "backup_retention_days": self.backup_retention_days,
            "tags": self.tags,
        }


@dataclass
class NoSQLTableRecord:
    """Normalized NoSQL table record (DynamoDB, CosmosDB, Firestore)."""
    table_name: str
    status: str = ""           # ACTIVE, CREATING, etc.
    item_count: int = 0
    size_bytes: int = 0
    region: str = ""
    billing_mode: str = ""     # PAY_PER_REQUEST, PROVISIONED
    read_capacity: int = 0
    write_capacity: int = 0
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "table_name": self.table_name,
            "status": self.status,
            "item_count": self.item_count,
            "size_bytes": self.size_bytes,
            "region": self.region,
            "billing_mode": self.billing_mode,
            "read_capacity": self.read_capacity,
            "write_capacity": self.write_capacity,
            "tags": self.tags,
        }


class DatabaseProvider(ProviderBase):
    """
    Abstract base for database resource queries.

    Each cloud provider implements these methods to list relational
    and NoSQL database instances.
    """

    @abstractmethod
    def list_db_instances(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[DBInstanceRecord]:
        """List all relational database instances (RDS, Azure SQL, Cloud SQL)."""
        pass

    @abstractmethod
    def list_nosql_tables(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[NoSQLTableRecord]:
        """List all NoSQL tables (DynamoDB, CosmosDB, Firestore)."""
        pass

    def find_publicly_accessible(
        self,
        instances: List[DBInstanceRecord],
    ) -> List[DBInstanceRecord]:
        """Find database instances that are publicly accessible (security check)."""
        return [db for db in instances if db.publicly_accessible]

    def find_unencrypted(
        self,
        instances: List[DBInstanceRecord],
    ) -> List[DBInstanceRecord]:
        """Find unencrypted database instances (security check)."""
        return [db for db in instances if not db.encrypted]

    def find_no_backup(
        self,
        instances: List[DBInstanceRecord],
    ) -> List[DBInstanceRecord]:
        """Find instances with no automated backups configured."""
        return [db for db in instances if db.backup_retention_days == 0]
