# kloudkompass/tui/prompts.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Centralized user prompts with Phase 2.6 navigation support.
# q/Q -> quit, b/B or 0 -> back

from typing import Optional, Tuple
from datetime import datetime

from kloudkompass.core.provider_factory import get_available_providers, is_provider_implemented
from kloudkompass.utils.parsers import validate_date_format, validate_date_range
from kloudkompass.core.exceptions import DateRangeError


BREAKDOWN_OPTIONS = ["total", "service", "usage", "daily"]
OUTPUT_OPTIONS = ["table", "plain", "json", "csv"]


def _check_navigation(choice: str) -> Optional[str]:
    """
    Check if input is a navigation intent.
    
    Returns:
        'back' for back navigation
        'quit' for quit navigation
        None for regular input
    """
    choice_lower = choice.lower()
    if choice_lower in ('q', 'quit'):
        return 'quit'
    if choice_lower in ('b', 'back'):
        return 'back'
    return None


def select_provider(
    current: Optional[str] = None,
    allow_back: bool = True,
) -> Tuple[Optional[str], str]:
    """
    Prompt user to select a cloud provider.
    
    Returns:
        Tuple of (selected_provider, action) where action is 'continue', 'back', or 'quit'
    """
    providers = get_available_providers()
    
    print("\nSelect Cloud Provider:")
    print("-" * 30)
    
    for i, provider in enumerate(providers, 1):
        marker = " *" if provider == current else ""
        # Phase 2.6: Show if provider is implemented
        if not is_provider_implemented(provider):
            status = " (Coming soon)"
        else:
            status = ""
        print(f"  {i}. {provider.upper()}{marker}{status}")
    
    if allow_back:
        print(f"  0. Back")
    
    print()
    print("  [Q] Quit")
    print()
    
    while True:
        choice = input("Enter choice: ").strip()
        
        # Check for navigation intent
        nav = _check_navigation(choice)
        if nav == 'quit':
            return None, "quit"
        if nav == 'back':
            return None, "back"
        
        if choice == "0" and allow_back:
            return None, "back"
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(providers):
                selected = providers[idx]
                # Phase 2.6: Block unimplemented providers
                if not is_provider_implemented(selected):
                    print(f"\n{selected.upper()} cost analysis is not yet available.")
                    print("Currently supported: AWS")
                    print("Press Enter to continue...")
                    input()
                    continue
                return selected, "continue"
        except ValueError:
            # Try matching by name
            choice_lower = choice.lower()
            if choice_lower in providers:
                if not is_provider_implemented(choice_lower):
                    print(f"\n{choice_lower.upper()} cost analysis is not yet available.")
                    print("Currently supported: AWS")
                    print("Press Enter to continue...")
                    input()
                    continue
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
        print("  (Enter 'back' or 0 to go back, 'q' to quit)")
    
    print()
    
    while True:
        default_hint = f" [{current}]" if current else ""
        date_str = input(f"Date (YYYY-MM-DD){default_hint}: ").strip()
        
        # Check navigation
        nav = _check_navigation(date_str)
        if nav == 'quit':
            return None, "quit"
        if nav == 'back' or date_str == "0":
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
    if action in ("back", "quit"):
        return None, None, action
    
    # End date
    end, action = input_date("Enter End Date:", current_end)
    if action in ("back", "quit"):
        return None, None, action
    
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
    print("  [Q] Quit")
    print()
    
    while True:
        choice = input("Enter choice: ").strip()
        
        nav = _check_navigation(choice)
        if nav == 'quit':
            return None, "quit"
        if nav == 'back':
            return None, "back"
        
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
    print("  Enter 'back' or 0 to go back, 'q' to quit")
    print()
    
    default_hint = f" [{current}]" if current is not None else " [0]"
    value = input(f"Threshold (USD){default_hint}: ").strip()
    
    nav = _check_navigation(value)
    if nav == 'quit':
        return None, "quit"
    if nav == 'back':
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
    print("  [Q] Quit")
    print()
    
    while True:
        choice = input("Enter choice: ").strip()
        
        nav = _check_navigation(choice)
        if nav == 'quit':
            return None, "quit"
        if nav == 'back':
            return None, "back"
        
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


def ensure_region_configured(session):
    """
    Interactive region gate — checks if region is set, prompts if not.

    Uses pure check_region_configured from provider_setup, then handles
    the interactive prompt here (where I/O is appropriate).

    Returns:
        RegionSetupResult with resolved region.
    """
    from kloudkompass.tui.provider_setup import (
        check_region_configured,
        apply_region_choice,
        RegionSetupResult,
        AWS_REGIONS,
        DEFAULT_REGION,
    )

    result = check_region_configured(session)
    if result.success:
        return result

    # Needs interactive prompt
    print("\n  ⚠ No region configured. Please select a region.")
    print(f"  Common regions: {', '.join(AWS_REGIONS[:4])}")
    print(f"  (Press Enter for default: {DEFAULT_REGION})\n")

    try:
        user_input = input("  Region: ").strip()
    except (EOFError, KeyboardInterrupt):
        return RegionSetupResult(
            success=False, region="", message="Region input cancelled."
        )

    region = user_input or DEFAULT_REGION
    return apply_region_choice(session, region)

