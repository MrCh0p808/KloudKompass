# bashcloud/infra/aws_cli_adapter.py
# ------------------------------------
# I handle all AWS CLI interactions here. This adapter encapsulates
# pagination, token management, and JSON parsing for Cost Explorer
# and other AWS services. Providers use this instead of calling
# the CLI directly.

import json
import re
import time
from typing import List, Dict, Any, Optional

from bashcloud.infra.base_adapter import BaseCloudAdapter
from bashcloud.core.exceptions import PaginationError, ParsingError
from bashcloud.utils.logger import debug


# Safety limit for pagination
MAX_PAGES = 100


class AWSCLIAdapter(BaseCloudAdapter):
    """
    AWS CLI adapter with pagination and Cost Explorer support.
    
    I handle all the complexity of calling aws commands, parsing JSON,
    and managing pagination tokens so cost providers stay clean.
    """
    
    CLI_NAME = "aws"
    PAGE_TOKEN_KEY = "NextPageToken"
    
    def __init__(self, timeout: int = 120):
        super().__init__(timeout)
        self._query_duration: float = 0.0
    
    @property
    def query_duration(self) -> float:
        """Duration of last query in seconds."""
        return self._query_duration
    
    def get_cli_version(self) -> Optional[str]:
        """
        Get AWS CLI version.
        
        I parse the output of 'aws --version' to extract the version number.
        Returns None if unable to determine.
        """
        try:
            result = self.run_command(["--version"], check=False)
            if result.success:
                # Output is like: aws-cli/2.15.0 Python/3.11.6 ...
                match = re.search(r"aws-cli/(\d+\.\d+\.\d+)", result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            pass
        return None
    
    def check_credentials(self) -> tuple[bool, Optional[str]]:
        """
        Check if AWS credentials are valid.
        
        I call 'aws sts get-caller-identity' which is a quick way to
        verify credentials without making any other API calls.
        """
        try:
            result = self.run_command(
                ["sts", "get-caller-identity", "--output", "json"],
                check=False,
            )
            if result.success:
                return (True, None)
            else:
                error = result.stderr.strip()
                if "ExpiredToken" in error:
                    return (False, "AWS credentials have expired")
                elif "InvalidClientTokenId" in error:
                    return (False, "AWS access key is invalid")
                elif "SignatureDoesNotMatch" in error:
                    return (False, "AWS secret key is invalid")
                else:
                    return (False, f"Credential check failed: {error[:100]}")
        except Exception as e:
            return (False, str(e))
    
    def check_cost_explorer_access(self) -> tuple[bool, Optional[str]]:
        """
        Check if Cost Explorer API is accessible.
        
        I make a minimal CE call to verify permissions. This catches
        Access Denied errors before the user runs a full query.
        """
        try:
            # I use a 1-day range yesterday to minimize costs
            from datetime import date, timedelta
            yesterday = date.today() - timedelta(days=1)
            start_str = yesterday.isoformat()
            end_str = date.today().isoformat()
            
            args = [
                "ce", "get-cost-and-usage",
                "--time-period", f"Start={start_str},End={end_str}",
                "--granularity", "DAILY",
                "--metrics", "UnblendedCost",
                "--output", "json",
            ]
            
            result = self.run_command(args, check=False)
            
            if result.success:
                return (True, None)
            else:
                error = result.stderr.strip()
                if "AccessDenied" in error or "UnauthorizedAccess" in error:
                    return (False, "ce:GetCostAndUsage permission denied")
                elif "OptInRequired" in error or "not enabled" in error.lower():
                    return (False, "Cost Explorer is not enabled for this account")
                else:
                    return (False, f"Cost Explorer check failed: {error[:100]}")
        except Exception as e:
            return (False, str(e))
    
    def get_cost_explorer_data(
        self,
        start_date: str,
        end_date: str,
        granularity: str = "MONTHLY",
        metrics: str = "UnblendedCost",
        group_by: Optional[List[Dict[str, str]]] = None,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch Cost Explorer data with automatic pagination.
        
        I handle all pagination internally, tracking tokens and merging
        ResultsByTime from all pages. Returns the combined response.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            granularity: DAILY or MONTHLY
            metrics: Cost metric (UnblendedCost, BlendedCost, etc.)
            group_by: Optional grouping specification
            profile: Optional AWS profile
            region: Optional AWS region
            
        Returns:
            Combined response dict with all ResultsByTime entries
        """
        start_time = time.perf_counter()
        
        # I build the base command
        base_args = [
            "ce", "get-cost-and-usage",
            "--time-period", f"Start={start_date},End={end_date}",
            "--granularity", granularity,
            "--metrics", metrics,
            "--output", "json",
        ]
        
        if group_by:
            base_args.extend(["--group-by", json.dumps(group_by)])
        
        if profile:
            base_args.extend(["--profile", profile])
        
        if region:
            base_args.extend(["--region", region])
        
        # I paginate through all results
        all_results_by_time: List[Dict[str, Any]] = []
        seen_tokens: set = set()
        current_token: Optional[str] = None
        response_metadata: Dict[str, Any] = {}
        self._page_count = 0
        
        debug(f"AWS CE query: {start_date} to {end_date}, granularity={granularity}")
        
        while True:
            self._page_count += 1
            
            if self._page_count > MAX_PAGES:
                raise PaginationError(
                    f"Exceeded maximum page count ({MAX_PAGES}). "
                    "Query may be returning too much data."
                )
            
            # I add token if we have one
            args = base_args.copy()
            if current_token:
                args.extend(["--next-token", current_token])
            
            result = self.run_command(args, check=True)
            
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                raise ParsingError(
                    f"Failed to parse AWS CE response page {self._page_count}: {e}",
                    raw_output=result.stdout[:500]
                )
            
            # I store metadata from first page
            if self._page_count == 1:
                response_metadata = {
                    k: v for k, v in data.items()
                    if k not in ("ResultsByTime", "NextPageToken")
                }
            
            # I collect results
            all_results_by_time.extend(data.get("ResultsByTime", []))
            
            # I check for next page
            next_token = data.get(self.PAGE_TOKEN_KEY)
            
            if not next_token:
                break
            
            # I detect infinite loops
            if next_token in seen_tokens:
                raise PaginationError(
                    f"Duplicate token in AWS CE on page {self._page_count}",
                    token=next_token
                )
            
            seen_tokens.add(next_token)
            current_token = next_token
        
        self._query_duration = time.perf_counter() - start_time
        
        debug(
            f"AWS CE query complete: {self._page_count} pages, "
            f"{len(all_results_by_time)} results, {self._query_duration:.2f}s"
        )
        
        return {
            **response_metadata,
            "ResultsByTime": all_results_by_time,
        }


# Singleton adapter instance
_aws_adapter: Optional[AWSCLIAdapter] = None


def get_aws_cli_adapter() -> AWSCLIAdapter:
    """Get the shared AWS CLI adapter instance."""
    global _aws_adapter
    if _aws_adapter is None:
        _aws_adapter = AWSCLIAdapter()
    return _aws_adapter
