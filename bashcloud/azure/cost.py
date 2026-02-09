# bashcloud/azure/cost.py
# ------------------------
# Azure Cost Management implementation stub.
# Follows the same structure as AWS to maintain consistency.
#
# To implement this module:
# 1. Use 'az consumption usage list' for usage data
# 2. Use 'az costmanagement query' for cost breakdowns
# 3. Handle Azure's date format requirements
# 4. Parse responses into CostRecord format
# 5. Handle subscription selection (az account show, az account set)

from typing import List, Optional

from bashcloud.core.cost_base import CostProvider, CostRecord
from bashcloud.core.exceptions import BashCloudError


class AzureCostProvider(CostProvider):
    """
    Azure implementation of the CostProvider interface.
    
    Uses the Azure CLI 'az consumption' and 'az costmanagement'
    commands to fetch billing data. Azure requires a subscription context.
    
    Note: Azure Cost Management API requires specific permissions.
    The user needs Reader role plus Cost Management Reader role.
    """
    
    provider_name = "Azure"
    cli_command = "az"
    
    def is_available(self) -> bool:
        """Check if Azure CLI is installed."""
        import shutil
        return shutil.which("az") is not None
    
    def validate_credentials(self) -> bool:
        """Check if Azure credentials are valid."""
        from bashcloud.core.health import check_azure_credentials
        is_valid, _ = check_azure_credentials()
        return is_valid
    
    def get_total_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get total cost for the date range.
        
        Uses: az consumption usage list --start-date X --end-date Y
        and aggregate the results.
        """
        raise BashCloudError(
            "Azure cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. Azure support coming soon."
        )
    
    def get_cost_by_service(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by service.
        
        Groups by 'meterCategory' which is Azure's equivalent
        of AWS service names.
        """
        raise BashCloudError(
            "Azure cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. Azure support coming soon."
        )
    
    def get_cost_by_usage_type(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by usage type.
        
        Groups by 'meterName' for granular usage breakdown.
        """
        raise BashCloudError(
            "Azure cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. Azure support coming soon."
        )
    
    def get_daily_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by day.
        """
        raise BashCloudError(
            "Azure cost queries are not yet implemented.",
            suggestion="Currently only AWS is supported. Azure support coming soon."
        )
