# kloudkompass/gcp/cost.py
# ----------------------
# GCP Billing implementation stub.
# Follows the same structure as AWS for consistency.
#
# To implement this module:
# 1. GCP billing data is not directly accessible via gcloud CLI
# 2. Need to export billing to BigQuery first
# 3. Then query BigQuery: bq query --use_legacy_sql=false 'SELECT ...'
# 4. Parse results into CostRecord format
#
# Alternative approach:
# 1. Use the Cloud Billing API via gcloud commands
# 2. gcloud billing accounts list
# 3. gcloud billing projects describe PROJECT_ID

from typing import List, Optional

from kloudkompass.core.cost_base import CostProvider, CostRecord
from kloudkompass.core.exceptions import KloudKompassError


class GCPCostProvider(CostProvider):
    """
    GCP implementation of the CostProvider interface.
    
    GCP billing is more complex than AWS. Detailed cost data requires
    exporting billing to BigQuery first. Can provide basic billing
    info via the Cloud Billing API.
    
    Note: The user needs billing.accounts.get and billing.accounts.list
    permissions to query billing data.
    """
    
    provider_name = "GCP"
    cli_command = "gcloud"
    
    def is_available(self) -> bool:
        """Check if gcloud CLI is installed."""
        import shutil
        return shutil.which("gcloud") is not None
    
    def validate_credentials(self) -> bool:
        is_valid, _ = check_gcp_credentials()
        return is_valid

    def get_manifest(self) -> dict:
        """Return the module manifest for the Adaptive Sidebar."""
        return {
            "cost": {
                "label": "GCP Billing",
                "icon": "💰",
                "id": "nav_cost_gcp"
            }
        }
    
    def get_total_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get total cost for the date range.
        
        GCP requires BigQuery export for detailed costs.
        May provide a basic estimate from the billing API.
        """
        raise KloudKompassError(
            "GCP cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. GCP support coming soon."
        )
    
    def get_cost_by_service(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """Get cost broken down by service."""
        raise KloudKompassError(
            "GCP cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. GCP support coming soon."
        )
    
    def get_cost_by_usage_type(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """Get cost broken down by usage type."""
        raise KloudKompassError(
            "GCP cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. GCP support coming soon."
        )
    
    def get_daily_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """Get cost broken down by day."""
        raise KloudKompassError(
            "GCP cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. GCP support coming soon."
        )
