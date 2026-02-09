# bashcloud/utils/parsers.py
# ---------------------------
# all input validation and response parsing handling.
# Date validation is critical because the cloud APIs have strict format
# requirements and error messages are often cryptic.

import re
from datetime import datetime, date
from typing import Tuple, Optional

from bashcloud.core.exceptions import DateRangeError


# ISO date format pattern YYYY-MM-DD
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date_format(date_str: str) -> bool:
    """
    Check if a string is a valid ISO date format.
    
    Checks both the pattern and that the values are valid calendar dates.
    "2024-02-30" matches the pattern but is not a real date.
    
    Returns:
        True if valid, False otherwise
    """
    if not DATE_PATTERN.match(date_str):
        return False
    
    try:
        parse_iso_date(date_str)
        return True
    except ValueError:
        return False


def parse_iso_date(date_str: str) -> date:
    """
    Parse an ISO date string into a date object.
    
    Args:
        date_str: Date in YYYY-MM-DD format
        
    Returns:
        datetime.date object
        
    Raises:
        ValueError: If the string is not a valid date
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def validate_date_range(start_str: str, end_str: str) -> Tuple[date, date]:
    """
    Validate a start and end date pair.
    
    Checks that both dates are valid format and that start is before or
    equal to end. Returns the parsed dates on success.
    
    Raises:
        DateRangeError: If validation fails
    """
    # Check format
    if not DATE_PATTERN.match(start_str):
        raise DateRangeError(
            f"Start date '{start_str}' is not in YYYY-MM-DD format."
        )
    
    if not DATE_PATTERN.match(end_str):
        raise DateRangeError(
            f"End date '{end_str}' is not in YYYY-MM-DD format."
        )
    
    # Parse dates
    try:
        start_date = parse_iso_date(start_str)
    except ValueError:
        raise DateRangeError(
            f"Start date '{start_str}' is not a valid calendar date."
        )
    
    try:
        end_date = parse_iso_date(end_str)
    except ValueError:
        raise DateRangeError(
            f"End date '{end_str}' is not a valid calendar date."
        )
    
    # Check order
    if start_date > end_date:
        raise DateRangeError(
            f"Start date ({start_str}) must be before or equal to end date ({end_str})."
        )
    
    return start_date, end_date


def parse_aws_cost_amount(amount_str: str) -> float:
    """
    Parse an AWS cost amount string to float.
    
    AWS returns amounts as strings like "54.2345678". Parses to float
    and round to 2 decimal places for display.
    """
    try:
        return round(float(amount_str), 2)
    except (ValueError, TypeError):
        return 0.0


def parse_aws_time_period(period: dict) -> str:
    """
    Extract a readable period string from AWS time period object.
    
    AWS returns {"Start": "2024-01-01", "End": "2024-02-01"}.
    Returns just the start date for display, or a range if needed.
    """
    start = period.get("Start", "")
    end = period.get("End", "")
    
    # For monthly granularity, just show the month
    if start and end:
        # If dates are in same month, show YYYY-MM
        if start[:7] == end[:7]:
            return start[:7]
        else:
            return f"{start[:7]} to {end[:7]}"
    
    return start or end or "Unknown"


def safe_get_nested(data: dict, *keys, default=None):
    """
    Safely get a nested dictionary value.
    
    This to avoid KeyError when API response structure varies.
    
    Example:
        safe_get_nested(data, "ResultsByTime", 0, "Total", "UnblendedCost")
    """
    current = data
    for key in keys:
        try:
            if isinstance(current, dict):
                current = current.get(key, default)
            elif isinstance(current, (list, tuple)) and isinstance(key, int):
                current = current[key] if len(current) > key else default
            else:
                return default
            
            if current is None:
                return default
        except (KeyError, IndexError, TypeError):
            return default
    
    return current
