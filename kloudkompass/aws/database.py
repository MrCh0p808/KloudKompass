# kloudkompass/aws/database.py
# ----------------------------
# AWS database provider implementation. Uses AWS CLI rds and
# dynamodb commands to list database resources.

from typing import List, Dict, Any, Optional

from kloudkompass.core.database_base import (
    DatabaseProvider, DBInstanceRecord, NoSQLTableRecord,
)
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.utils.subprocess_helpers import run_cli_json, build_aws_command
from kloudkompass.utils.logger import debug


class AWSDatabaseProvider(DatabaseProvider):
    """
    AWS RDS/DynamoDB implementation of the DatabaseProvider interface.

    Uses `aws rds describe-db-instances` for relational databases
    and `aws dynamodb list-tables` + `describe-table` for NoSQL.
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

    def list_db_instances(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[DBInstanceRecord]:
        """List all RDS database instances."""
        self._ensure_ready()
        debug("Fetching RDS instances...")

        command = build_aws_command("rds", "describe-db-instances",
                                    profile=profile, region=region)
        data = run_cli_json(command)
        instances: List[DBInstanceRecord] = []

        for db_data in data.get("DBInstances", []):
            # Extract endpoint info
            endpoint = db_data.get("Endpoint", {})
            endpoint_address = endpoint.get("Address", "") if endpoint else ""
            endpoint_port = endpoint.get("Port", 0) if endpoint else 0

            # Extract tags
            tags: Dict[str, str] = {}
            for tag in db_data.get("TagList", []):
                tags[tag.get("Key", "")] = tag.get("Value", "")

            instances.append(DBInstanceRecord(
                db_id=db_data.get("DBInstanceIdentifier", ""),
                engine=db_data.get("Engine", ""),
                engine_version=db_data.get("EngineVersion", ""),
                instance_class=db_data.get("DBInstanceClass", ""),
                status=db_data.get("DBInstanceStatus", ""),
                region=db_data.get("AvailabilityZone", ""),
                endpoint=endpoint_address,
                port=endpoint_port,
                storage_gb=db_data.get("AllocatedStorage", 0),
                multi_az=db_data.get("MultiAZ", False),
                encrypted=db_data.get("StorageEncrypted", False),
                publicly_accessible=db_data.get("PubliclyAccessible", False),
                backup_retention_days=db_data.get("BackupRetentionPeriod", 0),
                tags=tags,
            ))

        instances.sort(key=lambda d: d.db_id.lower())
        debug(f"Found {len(instances)} RDS instances")
        return instances

    def list_nosql_tables(
        self,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> List[NoSQLTableRecord]:
        """List all DynamoDB tables with details."""
        self._ensure_ready()
        debug("Fetching DynamoDB tables...")

        # First get table names
        command = build_aws_command("dynamodb", "list-tables",
                                    profile=profile, region=region)
        data = run_cli_json(command)
        table_names = data.get("TableNames", [])

        tables: List[NoSQLTableRecord] = []
        for table_name in table_names:
            try:
                # Get details for each table
                desc_command = build_aws_command("dynamodb", "describe-table",
                                                 profile=profile, region=region)
                desc_command.extend(["--table-name", table_name])
                desc_data = run_cli_json(desc_command)
                table_data = desc_data.get("Table", {})

                # Extract provisioned throughput
                throughput = table_data.get("ProvisionedThroughput", {})
                billing = table_data.get("BillingModeSummary", {})

                tables.append(NoSQLTableRecord(
                    table_name=table_data.get("TableName", table_name),
                    status=table_data.get("TableStatus", ""),
                    item_count=table_data.get("ItemCount", 0),
                    size_bytes=table_data.get("TableSizeBytes", 0),
                    region=region or "",
                    billing_mode=billing.get("BillingMode", "PROVISIONED"),
                    read_capacity=throughput.get("ReadCapacityUnits", 0),
                    write_capacity=throughput.get("WriteCapacityUnits", 0),
                ))
            except KloudKompassError:
                # If we can't describe a table, still include it with basic info
                tables.append(NoSQLTableRecord(
                    table_name=table_name,
                    status="UNKNOWN",
                    region=region or "",
                ))

        tables.sort(key=lambda t: t.table_name.lower())
        debug(f"Found {len(tables)} DynamoDB tables")
        return tables

    def start_db_instance(
        self,
        db_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        self._ensure_ready()
        command = build_aws_command("rds", "start-db-instance", profile=profile, region=region)
        command.extend(["--db-instance-identifier", db_id])
        try:
            run_cli_json(command)
            return True
        except KloudKompassError:
            return False

    def stop_db_instance(
        self,
        db_id: str,
        region: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> bool:
        self._ensure_ready()
        command = build_aws_command("rds", "stop-db-instance", profile=profile, region=region)
        command.extend(["--db-instance-identifier", db_id])
        try:
            run_cli_json(command)
            return True
        except KloudKompassError:
            return False
