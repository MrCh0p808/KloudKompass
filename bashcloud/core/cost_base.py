# bashcloud/core/cost_base.py
# ----------------------------
# the CostProvider abstract base definition. All cloud-specific cost modules
# inherit from this and implement these methods. The normalized output format
# ensures the CLI can display costs from any provider the same way.

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from bashcloud.core.provider_base import ProviderBase


@dataclass
class CostRecord:
    """
    Normalized cost record format.
    
    This dataclass so that cost data from AWS, Azure, and GCP all
    look the same to the CLI. Each provider's cost module transforms
    their native response into this format.
    """
    name: str          # Service name, usage type, or date depending on breakdown
    amount: float      # Cost amount as a float
    unit: str          # Currency unit (USD, EUR, etc)
    period: str        # Time period this cost covers (YYYY-MM or YYYY-MM-DD)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "name": self.name,
            "amount": self.amount,
            "unit": self.unit,
            "period": self.period,
        }


class CostProvider(ProviderBase):
    """
    Abstract base for cost query functionality.
    
    Each cloud provider implements these methods to fetch billing data.
    The return type is always List[CostRecord] so the CLI can handle
    all providers uniformly.
    """
    
    @abstractmethod
    def get_total_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get total cost for the date range.
        
        Returns a single CostRecord with the aggregated total.
        The name field will be "Total" or similar.
        """
        pass
    
    @abstractmethod
    def get_cost_by_service(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by service.
        
        Returns one CostRecord per service (EC2, S3, Lambda, etc).
        Sorted by cost descending so the expensive services are first.
        """
        pass
    
    @abstractmethod
    def get_cost_by_usage_type(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by usage type.
        
        Usage types are more granular than services. For AWS this might
        be things like "USW2-BoxUsage:t3.micro" showing exactly what
        instance types are costing money.
        """
        pass
    
    @abstractmethod
    def get_daily_cost(
        self,
        start_date: str,
        end_date: str,
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Get cost broken down by day.
        
        Returns one CostRecord per day in the range. The name field
        contains the date. Useful for spotting cost spikes.
        """
        pass
    
    def get_cost(
        self,
        start_date: str,
        end_date: str,
        breakdown: str = "total",
        profile: Optional[str] = None,
        region: Optional[str] = None,
    ) -> List[CostRecord]:
        """
        Convenience method that routes to the appropriate breakdown method.
        
        This as the main entry point so callers do not need to
        know which specific method to call. Just pass breakdown type.
        """
        breakdown_methods = {
            "total": self.get_total_cost,
            "service": self.get_cost_by_service,
            "usage": self.get_cost_by_usage_type,
            "daily": self.get_daily_cost,
        }
        
        method = breakdown_methods.get(breakdown.lower())
        if method is None:
            valid = ", ".join(breakdown_methods.keys())
            raise ValueError(f"Invalid breakdown '{breakdown}'. Valid options: {valid}")
        
        return method(start_date, end_date, profile, region)
    
    def filter_by_threshold(
        self,
        records: List[CostRecord],
        threshold: float,
    ) -> List[CostRecord]:
        """
        Filter out records below the cost threshold.
        
        This to hide tiny costs that just clutter the output.
        For example, threshold=1.0 hides anything under $1.
        """
        return [r for r in records if r.amount >= threshold]
