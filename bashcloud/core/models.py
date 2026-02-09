# bashcloud/core/models.py
# -------------------------
# I define the core data models here that all providers return.
# These dataclasses normalize output from AWS, Azure, and GCP so the
# CLI and formatters can handle them uniformly.

from dataclasses import dataclass, asdict
from typing import Dict, Any, ClassVar, List


@dataclass
class CostRecord:
    """
    Normalized cost record format.
    
    I use this dataclass so cost data from AWS, Azure, and GCP all
    look the same to the CLI. Each provider transforms their native
    response into this format.
    """
    name: str          # Service name, usage type, or date depending on breakdown
    amount: float      # Cost amount as a float
    unit: str          # Currency unit (USD, EUR, etc)
    period: str        # Time period this cost covers (YYYY-MM or YYYY-MM-DD)
    
    # I keep the expected keys here for validation
    REQUIRED_KEYS: ClassVar[List[str]] = ["name", "amount", "unit", "period"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON export.
        
        I use asdict so all fields become primitives suitable for JSON.
        """
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "CostRecord":
        """
        Create a CostRecord from a dictionary.
        
        I normalize keys and types here, raising ValueError on missing
        or invalid data so bad input gets caught early.
        """
        if not isinstance(d, dict):
            raise ValueError(f"Expected dict, got {type(d).__name__}")
        
        # I check all required keys are present
        missing = [k for k in cls.REQUIRED_KEYS if k not in d]
        if missing:
            raise ValueError(f"Missing required keys: {', '.join(missing)}")
        
        # I normalize amount to float, handling string input from APIs
        try:
            amount = float(d["amount"])
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid amount value: {d['amount']}") from e
        
        return cls(
            name=str(d["name"]),
            amount=amount,
            unit=str(d["unit"]),
            period=str(d["period"]),
        )
