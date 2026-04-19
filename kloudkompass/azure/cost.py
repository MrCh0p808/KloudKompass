# kloudkompass/azure/cost.py
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

from kloudkompass.core.cost_base import CostProvider, CostRecord
from kloudkompass.core.exceptions import KloudKompassError
from kloudkompass.infra.azure_cli_adapter import get_azure_cli_adapter
from kloudkompass.utils.logger import debug


class AzureCostProvider(CostProvider):
    """
    Azure implementation of the CostProvider interface.
    
    Uses `az rest` against Microsoft.CostManagement to bypass slow legacy
    parsers. Requires 'Cost Management Reader' roles on the subscription.
    """
    
    provider_name = "Azure"
    cli_command = "az"
    
    def __init__(self):
        self._adapter = get_azure_cli_adapter()

    def get_manifest(self) -> dict:
        return {
            "cost": {
                "label": "📉 Cost Mgmt",
                "tooltip": "Analyze Azure spending",
                "icon": "📉",
                "id": "nav_cost"
            }
        }
    
    def is_available(self) -> bool:
        """Check if Azure CLI is installed."""
        return self._adapter.is_available()
    
    def validate_credentials(self) -> bool:
        """Check if Azure credentials are valid."""
        is_valid, _ = self._adapter.check_credentials()
        return is_valid
        
    def _parse_cost_query(self, data: dict, name_column: str, default_name: str, period: str) -> List[CostRecord]:
        """
        Dynamically zip the columns to the 2D rows returned by Azure Cost Management.
        """
        records = []
        properties = data.get("properties", {})
        columns = properties.get("columns", [])
        rows = properties.get("rows", [])
        
        # Build index map dynamically as Azure can return permutations
        col_map = {col["name"]: idx for idx, col in enumerate(columns)}
        
        cost_idx = col_map.get("PreTaxCost")
        curr_idx = col_map.get("Currency")
        name_idx = col_map.get(name_column)
        
        if cost_idx is None or curr_idx is None:
            debug(f"Invalid Azure Cost format. Missing cost columns. Meta: {col_map}")
            return records
            
        for row in rows:
            name = str(row[name_idx]) if name_idx is not None else default_name
            amount = float(row[cost_idx])
            unit = str(row[curr_idx])
            
            # Formatting standard dates from YYYYMMDD to YYYY-MM-DD
            if name_column == "UsageDate" and len(name) == 8:
                name = f"{name[:4]}-{name[4:6]}-{name[6:]}"
                
            records.append(CostRecord(
                name=name,
                amount=amount,
                unit=unit,
                period=period
            ))
            
        # Standardize returns, sort high to low
        records.sort(key=lambda x: x.amount, reverse=True)
        return records
    
    def get_total_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """Get total cost for the date range."""
        sub = self._adapter.get_active_subscription(profile)
        data = self._adapter.query_cost_management(sub, start_date, end_date, granularity="None")
        return self._parse_cost_query(data, "", "Total", f"{start_date} -> {end_date}")
    
    def get_cost_by_service(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """Get cost broken down by service (ServiceName)."""
        sub = self._adapter.get_active_subscription(profile)
        grouping = [{"type": "Dimension", "name": "ServiceName"}]
        data = self._adapter.query_cost_management(sub, start_date, end_date, granularity="None", group_by=grouping)
        return self._parse_cost_query(data, "ServiceName", "Unknown", f"{start_date} -> {end_date}")
    
    def get_cost_by_usage_type(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """Get cost broken down by usage meter (Meter)."""
        sub = self._adapter.get_active_subscription(profile)
        grouping = [{"type": "Dimension", "name": "Meter"}]
        data = self._adapter.query_cost_management(sub, start_date, end_date, granularity="None", group_by=grouping)
        return self._parse_cost_query(data, "Meter", "Unknown Type", f"{start_date} -> {end_date}")
    
    def get_daily_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """Get cost broken down by day."""
        sub = self._adapter.get_active_subscription(profile)
        # We must group by UsageDate explicitly or Granularity=Daily does it
        data = self._adapter.query_cost_management(sub, start_date, end_date, granularity="Daily")
        
        records = self._parse_cost_query(data, "UsageDate", "Unknown Date", f"{start_date} -> {end_date}")
        # Sort chronologically for daily
        records.sort(key=lambda x: x.name)
        return records
