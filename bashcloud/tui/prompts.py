# bashcloud/tui/prompts.py
# -------------------------
# Centralized all user prompts. This keeps the screen code clean
# and ensures consistent validation across all wizards.

from typing import Optional, List, Tuple
from datetime import datetime

from bashcloud.core.provider_factory import get_available_providers
from bashcloud.utils.parsers import validate_date_format, validate_date_range
from bashcloud.core.exceptions import DateRangeError


BREAKDOWN_OPTIONS = ["total", "service", "usage", "daily"]
OUTPUT_OPTIONS = ["table", "plain", "json", "csv"]


def select_provider(
    current: Optional[str] = None,
    allow_back: bool = True,
) -> Tuple[Optional[str], str]:
    """
    Prompt user to select a cloud provider.
    
    Returns:
        Tuple of (selected_provider, action) where action is 'continue' or 'back'
    """
    providers = get_available_providers()
    
    print("\nSelect Cloud Provider:")
    print("-" * 30)
    
    for i, provider in enumerate(providers, 1):
        marker = " *" if provider == current else ""
        print(f"  {i}. {provider.upper()}{marker}")
    
    if allow_back:
        print(f"  0. Back")
    
    print()
    
    while True:
        choice = input("Enter choice: ").strip()
        
        if choice == "0" and allow_back:
            return None, "back"
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(providers):
                return providers[idx], "continue"
        except ValueError:
            # Try matching by name
            choice_lower = choice.lower()
            if choice_lower in providers:
                return choice_lower, "continue"
        
        print("Invalid choice. Try again.")


def input_date(
    prompt_text: str,
    current: Optional[str] = None,
    allow_back: bool = True,
) -> Tuple[Optional[str], str]:
    """
    Prompt for a date in YYYY-MM-DD format.
    
    Returns:
        Tuple of (date_string, action)
    """
    print(f"\n{prompt_text}")
    
    if current:
        print(f"  Current: {current}")
    
    if allow_back:
        print("  (Enter 'back' to go back)")
    
    print()
    
    while True:
        default_hint = f" [{current}]" if current else ""
        date_str = input(f"Date (YYYY-MM-DD){default_hint}: ").strip()
        
        if date_str.lower() == "back" and allow_back:
            return None, "back"
        
        if not date_str and current:
            return current, "continue"
        
        if validate_date_format(date_str):
            return date_str, "continue"
        
        print("Invalid date format. Use YYYY-MM-DD (e.g., 2024-01-15)")


def input_date_range(
    current_start: Optional[str] = None,
    current_end: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str], str]:
    """
    Prompt for start and end dates.
    
    Returns:
        Tuple of (start_date, end_date, action)
    """
    # Start date
    start, action = input_date("Enter Start Date:", current_start)
    if action == "back":
        return None, None, "back"
    
    # End date
    end, action = input_date("Enter End Date:", current_end)
    if action == "back":
        return None, None, "back"
    
    # Validate range
    try:
        validate_date_range(start, end)
        return start, end, "continue"
    except DateRangeError as e:
        print(f"\n[ERROR] {e}\n")
        return None, None, "retry"


def select_breakdown(current: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Prompt user to select cost breakdown type.
    
    Returns:
        Tuple of (breakdown_type, action)
    """
    print("\nSelect Cost Breakdown:")
    print("-" * 30)
    
    for i, option in enumerate(BREAKDOWN_OPTIONS, 1):
        marker = " *" if option == current else ""
        desc = {
            "total": "Aggregate total cost",
            "service": "Cost per AWS service",
            "usage": "Cost per usage type",
            "daily": "Daily cost trend",
        }.get(option, "")
        print(f"  {i}. {option.capitalize()}{marker} - {desc}")
    
    print(f"  0. Back")
    print()
    
    while True:
        choice = input("Enter choice: ").strip()
        
        if choice == "0":
            return None, "back"
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(BREAKDOWN_OPTIONS):
                return BREAKDOWN_OPTIONS[idx], "continue"
        except ValueError:
            choice_lower = choice.lower()
            if choice_lower in BREAKDOWN_OPTIONS:
                return choice_lower, "continue"
        
        print("Invalid choice. Try again.")


def input_threshold(current: Optional[float] = None) -> Tuple[Optional[float], str]:
    """
    Prompt for cost threshold filter.
    
    Returns:
        Tuple of (threshold, action)
    """
    print("\nCost Threshold Filter:")
    print("  (Hide costs below this amount)")
    print("  Enter 0 or leave blank for no filter")
    print("  Enter 'back' to go back")
    print()
    
    default_hint = f" [{current}]" if current is not None else " [0]"
    value = input(f"Threshold (USD){default_hint}: ").strip()
    
    if value.lower() == "back":
        return None, "back"
    
    if not value:
        return current if current is not None else 0.0, "continue"
    
    try:
        threshold = float(value)
        if threshold < 0:
            print("Threshold cannot be negative.")
            return None, "retry"
        return threshold, "continue"
    except ValueError:
        print("Invalid number. Enter a numeric value.")
        return None, "retry"


def select_output_format(current: Optional[str] = None) -> Tuple[Optional[str], str]:
    """
    Prompt user to select output format.
    
    Returns:
        Tuple of (format, action)
    """
    print("\nSelect Output Format:")
    print("-" * 30)
    
    for i, option in enumerate(OUTPUT_OPTIONS, 1):
        marker = " *" if option == current else ""
        print(f"  {i}. {option.capitalize()}{marker}")
    
    print(f"  0. Back")
    print()
    
    while True:
        choice = input("Enter choice: ").strip()
        
        if choice == "0":
            return None, "back"
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(OUTPUT_OPTIONS):
                return OUTPUT_OPTIONS[idx], "continue"
        except ValueError:
            choice_lower = choice.lower()
            if choice_lower in OUTPUT_OPTIONS:
                return choice_lower, "continue"
        
        print("Invalid choice. Try again.")


def confirm_action(message: str = "Proceed?", default: bool = True) -> bool:
    """
    Prompt for yes/no confirmation.
    """
    default_hint = "Y/n" if default else "y/N"
    response = input(f"\n{message} ({default_hint}): ").strip().lower()
    
    if not response:
        return default
    return response in ("y", "yes")
