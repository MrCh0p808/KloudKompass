# kloudkompass/aws/cost.py
# ----------------------
# the AWS Cost Explorer integration This is the real deal:
# subprocess calls to the AWS CLI, JSON parsing, pagination, and normalization
# into CostRecord format so the CLI can display it uniformly.

import json
from typing import List, Optional

from kloudkompass.core.cost_base import CostProvider, CostRecord
from kloudkompass.core.health import require_cli, require_credentials
from kloudkompass.core.exceptions import (
    KloudKompassError,
    PermissionDeniedError,
    ParsingError,
)
from kloudkompass.utils.subprocess_helpers import run_cli_command
from kloudkompass.utils.pagination import paginate_aws_cost_explorer
from kloudkompass.utils.parsers import (
    validate_date_range,
    parse_aws_cost_amount,
    parse_aws_time_period,
    safe_get_nested,
)
from kloudkompass.utils.logger import debug


class AWSCostProvider(CostProvider):
    """
    AWS implementation of the CostProvider interface.
    
    the AWS CLI 'ce' (Cost Explorer) commands used to fetch billing data.
    All results are normalized to CostRecord format so the CLI can handle
    them the same way regardless of provider.
    """
    
    provider_name = "AWS"
    cli_command = "aws"
    
    # Default granularity for different breakdown types
    # Monthly makes sense for service breakdown, daily for trend analysis
    DEFAULT_GRANULARITY = "MONTHLY"

    def get_manifest(self) -> dict:
        return {
            "cost": {
                "label": "💰 Billing",
                "tooltip": "View detailed AWS cost analysis",
                "icon": "💰",
                "id": "nav_cost"
            }
        }
    
    def is_available(self) -> bool:
        """Check if AWS CLI is installed."""
        import shutil
        return shutil.which("aws") is not None
    
    def validate_credentials(self) -> bool:
        """Check if AWS credentials are valid."""
        from kloudkompass.core.health import check_aws_credentials
        is_valid, _ = check_aws_credentials()
        return is_valid
    
    def _ensure_ready(self) -> None:
        """
        Verify CLI and credentials before making API calls.
        
        This calls this at the start of every cost method to fail fast
        with helpful error messages.
        """
        require_cli("aws")
        require_credentials("aws")
    
    def _build_base_command(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "MONTHLY",
        metrics: str = "UnblendedCost",
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[str]:
        """
        Build the base aws ce get-cost-and-usage command.
        
        Constructs the command with all required options here so the
        individual methods just need to add group-by clauses.
        """
        command = [
            "aws", "ce", "get-cost-and-usage",
            "--time-period", f"Start={start_date},End={end_date}",
            "--granularity", granularity,
            "--metrics", metrics,
            "--output", "json",
        ]
        
        if profile:
            command.extend(["--profile", profile])
        
        # Note: Cost Explorer is a global service, region is ignored
        # but Includes the option for consistency with other commands
        if region:
            command.extend(["--region", region])
        
        return command
    
    def _run_cost_query(
        self,
        command: List[str],
    ) -> dict:
        """
        Execute a cost query with pagination handling.
        
        the pagination helper used to handle multi-page responses.
        AWS CE can return large result sets for long date ranges.
        """
        debug(f"Running AWS CE command: {' '.join(command)}")
        
        try:
            result = paginate_aws_cost_explorer(command)
            return result
        except KloudKompassError as e:
            # Try to detect permission errors
            if "AccessDenied" in str(e) or "not authorized" in str(e).lower():
                raise PermissionDeniedError(
                    "aws",
                    required_permission="ce:GetCostAndUsage",
                    details=str(e)
                )
            raise
    
    def _parse_total_response(
        self,
        data: dict,
    ) -> List[CostRecord]:
        """
        Parse response for total cost (no grouping).
        
        This sums up the total across all time periods and return a single
        CostRecord with the aggregate.
        """
        results = data.get("ResultsByTime", [])
        
        if not results:
            debug("No results in AWS CE response")
            return [CostRecord(name="Total", amount=0.0, unit="USD", period="N/A")]
        
        total = 0.0
        unit = "USD"
        
        # Determine period range
        first_period = results[0].get("TimePeriod", {}).get("Start", "")
        last_period = results[-1].get("TimePeriod", {}).get("End", "")
        
        for period in results:
            # Total without groups is in period["Total"]["UnblendedCost"]
            amount_str = safe_get_nested(
                period, "Total", "UnblendedCost", "Amount", default="0"
            )
            unit = safe_get_nested(
                period, "Total", "UnblendedCost", "Unit", default="USD"
            )
            total += parse_aws_cost_amount(amount_str)
        
        period_str = f"{first_period} to {last_period}" if first_period else "Unknown"
        
        return [CostRecord(
            name="Total",
            amount=round(total, 2),
            unit=unit,
            period=period_str,
        )]
    
    def _parse_grouped_response(
        self,
        data: dict,
        group_type: str,
    ) -> List[CostRecord]:
        """
        Parse response with grouping (by service, usage type).
        
        AWS returns groups per time period. Aggregates across periods
        to get total per group, then sort by amount descending.
        """
        results = data.get("ResultsByTime", [])
        
        if not results:
            return []
        
        # Aggregate by group name across all periods
        aggregated = {}
        unit = "USD"
        
        for period in results:
            period_str = parse_aws_time_period(period.get("TimePeriod", {}))
            groups = period.get("Groups", [])
            
            for group in groups:
                # Keys is a list, usually just one element for single grouping
                keys = group.get("Keys", [])
                name = keys[0] if keys else "Unknown"
                
                # Get amount from metrics
                amount_str = safe_get_nested(
                    group, "Metrics", "UnblendedCost", "Amount", default="0"
                )
                unit = safe_get_nested(
                    group, "Metrics", "UnblendedCost", "Unit", default="USD"
                )
                amount = parse_aws_cost_amount(amount_str)
                
                if name in aggregated:
                    aggregated[name]["amount"] += amount
                else:
                    aggregated[name] = {"amount": amount, "unit": unit}
        
        # Determine period range for display
        first_period = results[0].get("TimePeriod", {}).get("Start", "")[:7]
        last_period = results[-1].get("TimePeriod", {}).get("End", "")[:7]
        period_display = f"{first_period} to {last_period}" if first_period else "Various"
        
        # Convert to CostRecords and sort
        records = [
            CostRecord(
                name=name,
                amount=round(data["amount"], 2),
                unit=data["unit"],
                period=period_display,
            )
            for name, data in aggregated.items()
        ]
        
        # Sort by amount descending so biggest costs are first
        records.sort(key=lambda r: r.amount, reverse=True)
        
        return records
    
    def _parse_daily_response(
        self,
        data: dict,
    ) -> List[CostRecord]:
        """
        Parse response for daily breakdown.
        
        Each time period is one day. Returns a CostRecord per day
        sorted chronologically.
        """
        results = data.get("ResultsByTime", [])
        
        records = []
        
        for period in results:
            period_info = period.get("TimePeriod", {})
            date_str = period_info.get("Start", "Unknown")
            
            amount_str = safe_get_nested(
                period, "Total", "UnblendedCost", "Amount", default="0"
            )
            unit = safe_get_nested(
                period, "Total", "UnblendedCost", "Unit", default="USD"
            )
            
            records.append(CostRecord(
                name=date_str,
                amount=parse_aws_cost_amount(amount_str),
                unit=unit,
                period=date_str,
            ))
        
        # Already chronological from API, but sort to be sure
        records.sort(key=lambda r: r.name)
        
        return records
    
    def get_total_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get total cost for the date range.
        
        This queries without any grouping to get the aggregate total.
        Returns a single CostRecord with the total amount.
        """
        self._ensure_ready()
        validate_date_range(start_date, end_date)
        
        command = self._build_base_command(
            start_date, end_date,
            granularity="MONTHLY",
            profile=profile,
            region=region,
        )
        
        data = self._run_cost_query(command)
        return self._parse_total_response(data)
    
    def get_cost_by_service(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by AWS service.
        
        Adds GROUP BY SERVICE to the query. Results are sorted by
        amount descending so expensive services are listed first.
        """
        self._ensure_ready()
        validate_date_range(start_date, end_date)
        
        command = self._build_base_command(
            start_date, end_date,
            granularity="MONTHLY",
            profile=profile,
            region=region,
        )
        
        # Add grouping by service
        command.extend([
            "--group-by", "Type=DIMENSION,Key=SERVICE"
        ])
        
        data = self._run_cost_query(command)
        return self._parse_grouped_response(data, "SERVICE")
    
    def get_cost_by_usage_type(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by usage type.
        
        Usage types are more granular than services. This shows exactly
        what resources are costing money, like specific instance types.
        """
        self._ensure_ready()
        validate_date_range(start_date, end_date)
        
        command = self._build_base_command(
            start_date, end_date,
            granularity="MONTHLY",
            profile=profile,
            region=region,
        )
        
        command.extend([
            "--group-by", "Type=DIMENSION,Key=USAGE_TYPE"
        ])
        
        data = self._run_cost_query(command)
        return self._parse_grouped_response(data, "USAGE_TYPE")
    
    def get_daily_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by day.
        
        Switches to DAILY granularity here. Each CostRecord represents
        one day's total cost. Useful for spotting cost spikes.
        """
        self._ensure_ready()
        validate_date_range(start_date, end_date)
        
        command = self._build_base_command(
            start_date, end_date,
            granularity="DAILY",
            profile=profile,
            region=region,
        )
        
        data = self._run_cost_query(command)
        return self._parse_daily_response(data)
