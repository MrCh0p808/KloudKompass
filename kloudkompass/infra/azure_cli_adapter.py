# kloudkompass/infra/azure_cli_adapter.py
# ---------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Azure-specific CLI adapter for Cost Management API queries using `az rest`.

import json
import time
import re
from typing import List, Dict, Any, Optional

from kloudkompass.infra.base_adapter import BaseCloudAdapter
from kloudkompass.core.exceptions import ParsingError
from kloudkompass.utils.logger import debug


class AzureCLIAdapter(BaseCloudAdapter):
    """
    Azure CLI adapter with fast REST query execution.
    
    Wraps the `az` CLI. Specifically utilizes `az rest` for calling
    the Microsoft.CostManagement/query API directly, skipping the
    slower `az consumption` parsers.
    """
    
    CLI_NAME = "az"
    
    def __init__(self, timeout: int = 120):
        super().__init__(timeout)
        self._query_duration: float = 0.0
    
    @property
    def query_duration(self) -> float:
        """Duration of last query in seconds."""
        return self._query_duration
    
    def get_cli_version(self) -> Optional[str]:
        """Get Azure CLI version."""
        try:
            result = self.run_command(["--version"], check=False)
            if result.success:
                # Output resembles: azure-cli                         2.55.0
                match = re.search(r"azure-cli\s+(\d+\.\d+\.\d+)", result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None
    
    def check_credentials(self) -> tuple[bool, Optional[str]]:
        """
        Check if Azure credentials are valid and return an active subscription.
        """
        try:
            result = self.run_command(
                ["account", "show", "--output", "json"],
                check=False,
            )
            if result.success:
                return (True, None)
            else:
                error = result.stderr.strip()
                if "Please run 'az login'" in error:
                    return (False, "Azure credentials have expired or not logged in.")
                return (False, f"Credential check failed: {error[:100]}")
        except Exception as e:
            return (False, str(e))
            
    def get_active_subscription(self, profile: Optional[str] = None) -> str:
        """Helper to get the current or supplied subscription ID."""
        if profile:
            return profile
        
        # Load default
        result = self.run_command(["account", "show", "--query", "id", "-o", "tsv"], check=True)
        return result.stdout.strip()
        
    def query_cost_management(
        self,
        subscription_id: str,
        start_date: str,
        end_date: str,
        granularity: str = "None",
        group_by: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch Azure Cost Management data via fast `az rest`.
        
        Args:
            subscription_id: The target subscription GUI or profile ID.
            start_date: Start date YYYY-MM-DD
            end_date: End date YYYY-MM-DD
            granularity: "Daily" or "Monthly" or "None"
            group_by: Optional Cost Management grouping schema.
            
        Returns:
            Dict containing Azure's raw 2D query grid payload.
        """
        start_time = time.perf_counter()
        
        uri = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2023-11-01"
        
        body = {
            "type": "Usage",
            "timeframe": "Custom",
            "timePeriod": {
                "from": f"{start_date}T00:00:00Z",
                "to": f"{end_date}T23:59:59Z"
            },
            "dataset": {
                "granularity": granularity,
                "aggregation": {
                    "totalCost": {
                        "name": "PreTaxCost",
                        "function": "Sum"
                    }
                }
            }
        }
        
        if group_by:
            body["dataset"]["grouping"] = group_by

        args = [
            "rest",
            "--method", "post",
            "--uri", uri,
            "--body", json.dumps(body)
        ]
        
        debug(f"Azure Cost query: sub={subscription_id}, {start_date} to {end_date}, granularity={granularity}")
        
        result = self.run_command(args, check=True)
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ParsingError(
                f"Failed to parse Azure Cost response: {e}",
                raw_output=result.stdout[:500]
            )
            
        self._query_duration = time.perf_counter() - start_time
        debug(f"Azure Cost query complete: {self._query_duration:.2f}s")
        
        return data

# Singleton adapter instance
_azure_adapter: Optional[AzureCLIAdapter] = None

def get_azure_cli_adapter() -> AzureCLIAdapter:
    """Get the shared Azure CLI adapter instance."""
    global _azure_adapter
    if _azure_adapter is None:
        _azure_adapter = AzureCLIAdapter()
    return _azure_adapter
